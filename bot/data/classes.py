import sqlite3
import datetime as dt
from telebot.types import *
from telebot import TeleBot
from bot.data.functions import *
import json


class VideoHoster:
    def __init__(self, bot: TeleBot, do_log: bool, hoster: str):
        self.bot = bot
        self.l = do_log
        self.hoster = hoster

    def greet(self, message: Message) -> None:
        try:
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Загрузить видео"))
            if self.l:
                log_all(message.chat.id)
            self.clear_history(message)
            self.bot.send_message(message.chat.id, "Привет!", reply_markup=markup)
            self.bot.register_next_step_handler(message, self.menu)
        except Exception as err:
            self.bot.send_message(self.hoster, f"Ошибка у пользователя {message.chat.id}: {err}")

    def menu(self, message: Message) -> None:
        if self.filter_messages(message):
            return
        markup = ReplyKeyboardMarkup()
        markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Загрузить видео"))
        try:
            with open(f"logs/dialog_log_{message.chat.id}.json", mode="r", encoding="utf-8") as dialog_log:
                messages = json.load(dialog_log)
        except json.decoder.JSONDecodeError:
            messages = []
        messages.append({"role": "user", "content": message.text})
        bot_text = "Извините, я вас не понял. Выберите одну из опций на вашей клавиатуре! 😉"
        messages.append({"role": "assistant", "content": bot_text})
        log_dialog(messages, message.chat.id)

        self.bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.menu)

    def filter_messages(self, message: Message) -> bool:
        filtered = False
        with open("data/blacklist.txt", mode="r") as file:
            if str(message.chat.id) in file.read():
                self.bot.send_message(message.chat.id, "Извините, вы находитесь в чёрном списке бота")
                return True
        match message.text:
            case "/start":
                self.greet(message)
                filtered = True
            case "📺 Смотреть видео":
                self.bot.send_message(message.chat.id, "Загружаю доступные видео! :D",
                                      reply_markup=ReplyKeyboardRemove())
                self.watch(message)
                filtered = True
            case "📹 Загрузить видео":
                self.bot.send_message(message.chat.id, "Пришлите своё видео! :)", reply_markup=ReplyKeyboardRemove())
                self.bot.register_next_step_handler(message, self.send_video)
                filtered = True
        return filtered

    def watch(self, message: Message):
        ...

    def send_video(self, message: Message) -> None:
        if message.content_type == "video":
            if message.video.duration > 60:
                self.bot.send_message(message.chat.id, "Извините, но ваше видео слишком длинное!")
                self.menu(message)
                return
            date = dt.datetime.now()
            con = sqlite3.connect("db/VideoHoster.db")
            cur = con.cursor()
            cur.execute(f"""
            INSERT INTO Videos (
                       message_id,
                       author_id,
                       day,
                       month,
                       year
                   )
                   VALUES (
                       "{message.id}",
                       "{message.chat.id}",
                       "{date.day}",
                       "{date.month}",
                       "{date.year}"
                   );
                    """)
            con.commit()
            with open(f"videos/{message.chat.id}_{message.id}.mp4", mode="wb") as video_file:
                file_info = self.bot.get_file(message.video.file_id)
                video_file.write(self.bot.download_file(file_info.file_path))
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Загрузить видео"))
            self.bot.send_message(message.chat.id, "Видео успешно загружено на сервер!", reply_markup=markup)
            self.bot.register_next_step_handler(message, self.menu)
            return
        self.menu(message)

    def clear_history(self, message: Message):
        try:
            with open(f"logs/dialog_log_{message.chat.id}.json", mode="w", encoding="utf-8"):
                pass
        except Exception as err:
            self.bot.send_message(self.hoster, f"Ошибка у пользователя {message.chat.id}: {err}")

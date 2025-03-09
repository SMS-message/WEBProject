import datetime as dt
from random import shuffle

from telebot.types import *
from telebot import TeleBot
from data.functions import *
import json


class VideoHoster:
    def __init__(self, bot: TeleBot, do_log: bool, hoster: str):
        self.bot = bot
        self.l = do_log
        self.hoster = hoster

    def greet(self, message: Message) -> None:
        try:
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
            if self.l:
                log_all(message.chat.id)
            if not user_table_exists(message.chat.id):
                create_user_table(message.chat.id)
            else:
                update_user_table(message.chat.id)
            self.clear_history(message)
            self.bot.send_message(message.chat.id, "Привет!", reply_markup=markup)
            self.bot.register_next_step_handler(message, self.menu)
        except Exception as err:
            self.bot.send_message(self.hoster, f"Ошибка у пользователя {message.chat.id}: {err}")

    def menu(self, message: Message) -> None:
        if self.filter_messages(message):
            return
        markup = ReplyKeyboardMarkup()
        markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
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
            case "📹 Зайти в студию":
                self.studio(message)
                filtered = True
            case "📼 Просмотреть загруженные вами видео":
                ...
            case "📹 Загрузить видео":
                self.bot.send_message(message.chat.id,"Пришлите своё видео :)", reply_markup=ReplyKeyboardRemove())
                self.bot.register_next_step_handler(message, self.receive_video)
                filtered = True
            case "🎥 Загрузить несколько видео":
                self.bot.send_message(message.chat.id, "Хорошо, когда закончите напишите команду /stop", reply_markup=ReplyKeyboardRemove())
                self.bot.register_next_step_handler(message, self.receive_many_videos)
                filtered = True
            case "◀ Назад":
                markup = ReplyKeyboardMarkup()
                markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
                self.bot.send_message(message.chat.id,
                                      f"Хорошо, что вы хотите сделать?",
                                      reply_markup=markup)
                self.bot.register_next_step_handler(message, self.menu)
                filtered = True

        return filtered

    def receive_many_videos(self, message: Message):
        if message.text == "/stop":
            self.studio(message)
            return
        self.receive_video(message, True)
        self.bot.register_next_step_handler(message, self.receive_many_videos)

    def watch(self, message: Message):
        update_user_table(message.chat.id)
        queue = make_queue(message.chat.id)
        shuffle(queue)
        self.send_video(message, queue)

    def send_video(self, message: Message, queue: List[int]):
        if not queue:
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Загрузить видео"))
            self.bot.send_message(message.chat.id, "В вашей очереди закончились видео, приходите снова!",
                                  reply_markup=markup)
            self.bot.register_next_step_handler(message, self.menu)
            return

        con = sqlite3.connect("db/VideoHoster.db")
        cur = con.cursor()
        res = tuple(cur.execute(f"""SELECT message_id,
                                                       author_id
                                                  FROM Videos
                                                 WHERE ID = "{queue[0]}";
                                                """))
        message_id, author_id = res[0]
        # markup = InlineKeyboardMarkup()
        # markup.row(InlineKeyboardButton(text="♥", callback_data="like"),
        #            InlineKeyboardButton(text="👎", callback_data="dislike"),
        #            InlineKeyboardButton(text="⏩", callback_data="next"))
        markup = ReplyKeyboardMarkup()
        markup.row(KeyboardButton("❤"),
                   KeyboardButton("👎"),
                   KeyboardButton("⏩"))
        with open(f"videos/{author_id}_{message_id}.mp4", mode="rb") as video:
            self.bot.send_video(message.chat.id, video, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.update_db_by_reaction, queue)

    def update_db_by_reaction(self, message: Message, queue: List[int]):
        con = sqlite3.connect("db/VideoHoster.db")
        cur = con.cursor()
        if self.filter_messages(message):
            return
        match message.text:
            case "❤":
                cur.execute(f"""UPDATE Videos
                                   SET likes = likes + 1
                                 WHERE ID = "{queue[0]}";
                                """)
            case "👎":
                cur.execute(f"""UPDATE Videos
                                   SET dislikes = dislikes + 1
                                 WHERE ID = "{queue[0]}";
                                """)
        cur.execute(f"""UPDATE User_{message.chat.id}
                           SET viewed = 1
                         WHERE ID = "{queue[0]}";
                        """)
        con.commit()

        self.send_video(message, queue[1:])

    def studio(self, message: Message):
        markup = ReplyKeyboardMarkup()
        markup.row(KeyboardButton("📼 Просмотреть загруженные вами видео"), KeyboardButton("📹 Загрузить видео"))
        markup.row(KeyboardButton("🎥 Загрузить несколько видео"), KeyboardButton("◀ Назад"))
        self.bot.send_message(message.chat.id, f"Добро пожаловать в студию, {message.chat.first_name}!",
                              reply_markup=markup)
        self.bot.register_next_step_handler(message, self.filter_messages)

    def receive_video(self, message: Message, many: bool=False) -> None:
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
            self.bot.send_message(message.chat.id, "Видео успешно загружено на сервер!")
            if not many:
                self.studio(message)
            return
        self.menu(message)

    def clear_history(self, message: Message):
        try:
            with open(f"logs/dialog_log_{message.chat.id}.json", mode="w", encoding="utf-8"):
                pass
        except Exception as err:
            self.bot.send_message(self.hoster, f"Ошибка у пользователя {message.chat.id}: {err}")

from telebot.types import *
from telebot import TeleBot
from data.functions import *
import json


class MyBot:
    def __init__(self, bot: TeleBot, do_log: bool, hoster: str):
        self.bot = bot
        self.l = do_log
        self.hoster = hoster

    def greet(self, message: Message) -> None:
        try:
            if self.l:
                log_all(message.chat.id)
            self.clear_history(message)
            self.bot.send_message(message.chat.id, "Привет!")
            self.bot.register_next_step_handler(message, self.idle)
        except Exception as err:
            self.bot.send_message(self.hoster, f"Ошибка у пользователя {message.chat.id}: {err}")

    def idle(self, message: Message) -> None:
        if self.filter_messages(message):
            return
        try:
            with open(f"logs/dialog_log_{message.chat.id}.json", mode="r", encoding="utf-8") as dialog_log:
                messages = json.load(dialog_log)
        except json.decoder.JSONDecodeError:
            messages = []
        messages.append({"role": "user", "content": message.text})
        bot_text = message.text
        messages.append({"role": "assistant", "content": bot_text})
        log_dialog(messages, message.chat.id)

        self.bot.send_message(message.chat.id, bot_text)
        self.bot.register_next_step_handler(message, self.idle)

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

        return filtered

    def clear_history(self, message: Message):
        try:
            with open(f"logs/dialog_log_{message.chat.id}.json", mode="w", encoding="utf-8"):
                pass
        except Exception as err:
            self.bot.send_message(self.hoster, f"Ошибка у пользователя {message.chat.id}: {err}")

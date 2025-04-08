import datetime as dt
from random import shuffle
from telebot.types import *
from telebot import TeleBot
from .functions import *
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
            markup.resize_keyboard = True
            if not user_table_exists(message.chat.id):
                create_user_table(message.chat.id)
            else:
                update_user_table(message.chat.id)
            bot_text = "Привет!"
            if self.l:
                self.log(message, bot_text)
            self.bot.send_message(message.chat.id, bot_text, reply_markup=markup)
            self.bot.register_next_step_handler(message, self.menu)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода greet(): {err}")

    def menu(self, message: Message) -> None:
        if self.filter_messages(message):
            return
        markup = ReplyKeyboardMarkup()
        markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
        markup.resize_keyboard = True

        bot_text = "Извините, я вас не понял. Выберите одну из опций на вашей клавиатуре! 😉"

        self.log(message, bot_text)
        self.bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        self.bot.register_next_step_handler(message, self.menu)

    def filter_messages(self, message: Message) -> bool:
        filtered = False
        bot_text: str = ""
        with open("data/blacklist.txt", mode="r") as file:
            if str(message.chat.id) in file.read():
                bot_text = "Извините, вы находитесь в чёрном списке бота"
                self.bot.send_message(message.chat.id, bot_text)
                self.log(message, bot_text)
                return True
        match message.text:
            case "/start":
                self.greet(message)
                return True
            case "📺 Смотреть видео":
                bot_text = "Загружаю доступные видео! :D"
                self.bot.send_message(message.chat.id, bot_text,
                                      reply_markup=ReplyKeyboardRemove())
                self.watch(message)
                filtered = True
            case "📹 Зайти в студию":  #TODO: Чёт придумать со студией
                markup = ReplyKeyboardMarkup()
                markup.row(KeyboardButton("📼 Просмотреть загруженные вами видео"), KeyboardButton("📹 Загрузить видео"))
                markup.row(KeyboardButton("🎥 Загрузить несколько видео"), KeyboardButton("◀ Назад"))
                bot_text = f"Добро пожаловать в студию, {message.chat.first_name}!"
                self.bot.send_message(message.chat.id, bot_text,
                                      reply_markup=markup)
                self.bot.register_next_step_handler(message, self.filter_messages)
                filtered = True
            case "📼 Просмотреть загруженные вами видео":
                ...
            case "📹 Загрузить видео":
                bot_text = "Пришлите своё видео :)"
                self.bot.send_message(message.chat.id, bot_text, reply_markup=ReplyKeyboardRemove())
                self.bot.register_next_step_handler(message, self.receive_video)
                filtered = True
            case "🎥 Загрузить несколько видео":
                bot_text = "Хорошо, когда закончите напишите команду /stop"
                self.bot.send_message(message.chat.id, bot_text,
                                      reply_markup=ReplyKeyboardRemove())
                self.bot.register_next_step_handler(message, self.receive_many_videos)
                filtered = True
            case "◀ Назад":
                markup = ReplyKeyboardMarkup()
                markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
                markup.resize_keyboard = True

                bot_text = "Хорошо, что вы хотите сделать?"
                self.bot.send_message(message.chat.id,
                                      bot_text,
                                      reply_markup=markup)
                self.bot.register_next_step_handler(message, self.menu)
                filtered = True
        if self.l and bot_text:
            self.log(message, bot_text)
        return filtered

    def receive_many_videos(self, message: Message):
        if message.text == "/stop":
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("📼 Просмотреть загруженные вами видео"), KeyboardButton("📹 Загрузить видео"))
            markup.row(KeyboardButton("🎥 Загрузить несколько видео"), KeyboardButton("◀ Назад"))
            bot_text = f"Добро пожаловать в студию, {message.chat.first_name}!"
            self.bot.send_message(message.chat.id, bot_text,
                                  reply_markup=markup)
            self.bot.register_next_step_handler(message, self.filter_messages)
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
            markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
            markup.resize_keyboard = True

            bot_text = "В вашей очереди закончились видео, приходите снова!"
            self.log(message, bot_text)
            self.bot.send_message(message.chat.id, bot_text,
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
        markup.resize_keyboard = True
        video_filename = f"videos/{author_id}_{message_id}.mp4"
        with open(video_filename, mode="rb") as video:
            self.log(message, video_filename)
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

    def receive_video(self, message: Message, many: bool = False) -> None:
        if message.content_type == "video":
            if message.video.duration > 60:
                bot_text = "Извините, но ваше видео слишком длинное!"
                self.log(message, bot_text)
                self.bot.send_message(message.chat.id, bot_text)
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
            video_filename = f"videos/{message.chat.id}_{message.id}.mp4"
            with open(video_filename, mode="wb") as video_file:
                file_info = self.bot.get_file(message.video.file_id)
                video_file.write(self.bot.download_file(file_info.file_path))
            message.text = video_filename
            bot_text = "Видео успешно загружено на сервер!"
            self.log(message, bot_text)
            self.bot.send_message(message.chat.id, bot_text)
            if not many:
                markup = ReplyKeyboardMarkup()
                markup.row(KeyboardButton("📼 Просмотреть загруженные вами видео"), KeyboardButton("📹 Загрузить видео"))
                markup.row(KeyboardButton("🎥 Загрузить несколько видео"), KeyboardButton("◀ Назад"))
                bot_text = f"Добро пожаловать в студию, {message.chat.first_name}!"
                self.bot.send_message(message.chat.id, bot_text,
                                      reply_markup=markup)
                self.bot.register_next_step_handler(message, self.filter_messages)
            return
        self.menu(message)

    def log(self, message: Message, bot_reaction: str) -> None:
        try:
            filename = f"logs/user_{message.chat.id}.json"
            cur_dialog = [{
                            "role": "user",
                            "content": message.text,
                        },
                        {
                            "role": "assistant",
                            "content": bot_reaction
                        }]
            if os.path.exists(filename):
                log_file_read = open(filename, mode="r", encoding="utf-8")
                history: List = json.load(log_file_read)
                log_file_read.close()
            else:
                history = []
            with open(filename, mode="w", encoding="utf-8") as log_file:
                history.extend(cur_dialog)
                json.dump(history, log_file, ensure_ascii=False, indent=2)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода log(): {err}")

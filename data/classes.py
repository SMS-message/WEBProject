import datetime as dt
from random import shuffle
from telebot.types import *
from telebot import TeleBot
from .functions import *
from .db_session import create_session
from .videos import Videos
import json

class VideoHoster:
    def __init__(self, bot: TeleBot, do_log: bool, hoster: str, path_to_db: str):
        """
        Initialization

        :param bot: Телебот, с которым всё должно работать
        :param do_log: Параметр включающий/выключающий логирование
        :param hoster: ID хостера в телеграмм
        :param path_to_db: Путь до базы данных
        """
        self.bot = bot
        self.l = do_log
        self.hoster = hoster
        self.ptd = path_to_db

    def greet(self, message: Message) -> None:
        try:
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
            markup.resize_keyboard = True
            if not user_table_exists(message.chat.id, self.ptd):
                create_user_table(message.chat.id, self.ptd)
            else:
                update_user_table(message.chat.id, self.ptd)
            bot_text = "Привет!"
            if self.l:
                self.log(message.text, message.chat.id, bot_text)
            self.bot.send_message(message.chat.id, bot_text, reply_markup=markup)
            self.bot.register_next_step_handler(message, self.menu)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода greet(): {err}")

    def menu(self, message: Message) -> None:
        try:
            if self.filter_messages(message):
                return
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
            markup.resize_keyboard = True

            bot_text = "Извините, я вас не понял. Выберите одну из опций на вашей клавиатуре! 😉"

            self.log(message.text, message.chat.id, bot_text)
            self.bot.send_message(message.chat.id, bot_text, reply_markup=markup)
            self.bot.register_next_step_handler(message, self.menu)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода menu(): {err}")

    def studio(self, message: Message):
        try:
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("📼 Просмотреть загруженные вами видео"), KeyboardButton("📹 Загрузить видео"))
            markup.row(KeyboardButton("🎥 Загрузить несколько видео"), KeyboardButton("◀ Назад"))
            bot_text = f"Добро пожаловать в студию, {message.chat.first_name}!"
            self.log(message.text, message.chat.id, bot_text)
            self.bot.send_message(message.chat.id, bot_text,
                                  reply_markup=markup)
            self.bot.register_next_step_handler(message, self.filter_messages)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода studio(): {err}")

    def filter_messages(self, message: Message) -> bool:
        try:
            filtered = False
            bot_text: str = ""
            with open("./data/blacklist.txt", mode="r") as file:
                if str(message.chat.id) in file.read():
                    bot_text = "Извините, вы находитесь в чёрном списке бота"
                    self.bot.send_message(message.chat.id, bot_text)
                    self.log(message.text, message.chat.id, bot_text)
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
                case "📹 Зайти в студию":
                    self.studio(message)
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
                self.log(message.text, message.chat.id, bot_text)
            return filtered
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода filter_messages(): {err}")
    def receive_many_videos(self, message: Message):
        try:
            if message.text == "/stop":
                self.studio(message)
                return
            self.receive_video(message, True)
            self.bot.register_next_step_handler(message, self.receive_many_videos)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода receive_many_videos(): {err}")
    def watch(self, message: Message):
        try:
            update_user_table(message.chat.id, self.ptd)
            queue = make_queue(message.chat.id, self.ptd)
            shuffle(queue)
            self.send_video(message, queue)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода watch(): {err}")

    def send_video(self, message: Message, queue: List[int]):
        try:
            if not queue:
                markup = ReplyKeyboardMarkup()
                markup.row(KeyboardButton("📺 Смотреть видео"), KeyboardButton("📹 Зайти в студию"))
                markup.resize_keyboard = True

                bot_text = "В вашей очереди закончились видео, приходите снова!"
                self.log(message.text, message.chat.id, bot_text)
                self.bot.send_message(message.chat.id, bot_text,
                                      reply_markup=markup)
                self.bot.register_next_step_handler(message, self.menu)
                return

            session = create_session()
            res = session.query(Videos).get(queue[0])

            message_id, author_id = res.message_id, res.author_id
            markup = ReplyKeyboardMarkup()
            markup.row(KeyboardButton("❤"),
                       KeyboardButton("👎"),
                       KeyboardButton("⏩"))
            markup.resize_keyboard = True
            video_filename = f"./videos/{author_id}_{message_id}.mp4"
            with open(video_filename, mode="rb") as video:
                self.log(message.text, message.chat.id, video_filename)
                self.bot.send_video(message.chat.id, video, reply_markup=markup)
            self.bot.register_next_step_handler(message, self.update_db_by_reaction, queue)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода send_video(): {err}")
    def update_db_by_reaction(self, message: Message, queue: List[int]):
        try:
            session = create_session()
            if self.filter_messages(message):
                return
            match message.text:
                case "❤️":
                    session.query(Videos).filter(Videos.ID == queue[0]).update({Videos.likes: Videos.likes + 1})
                case "👎":
                    session.query(Videos).filter(Videos.ID == queue[0]).update({Videos.dislikes: Videos.dislikes + 1})
            session.commit()
            con = sqlite3.connect(self.ptd)
            cur = con.cursor()

            cur.execute(f"""UPDATE User_{message.chat.id}
                                   SET viewed = 1
                                 WHERE ID = "{queue[0]}";
                                """)
            con.commit()

            self.send_video(message, queue[1:])
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода update_db_by_reaction(): {err}")

    def receive_video(self, message: Message, many: bool = False) -> None:
        try:
            if message.content_type == "video":
                if message.video.duration > 60:
                    bot_text = "Извините, но ваше видео слишком длинное!"
                    self.log(message.text, message.chat.id, bot_text)
                    self.bot.send_message(message.chat.id, bot_text)
                    self.menu(message)
                    return
                date = dt.datetime.now()

                session = create_session()
                video = Videos()
                video.message_id = message.id
                video.author_id = message.chat.id
                video.day = date.day
                video.month = date.month
                video.year = date.year
                session.add(video)
                session.commit()

                video_filename = f"./videos/{message.chat.id}_{message.id}.mp4"
                with open(video_filename, mode="wb") as video_file:
                    file_info = self.bot.get_file(message.video.file_id)
                    video_file.write(self.bot.download_file(file_info.file_path))
                message.text = video_filename
                bot_text = "Видео успешно загружено на сервер!"
                self.log(message.text, message.chat.id, bot_text)
                self.bot.send_message(message.chat.id, bot_text)
                if not many:
                    self.studio(message)
                return
            self.menu(message)
        except Exception as err:
            self.bot.send_message(self.hoster,
                                  f"Ошибка у пользователя {message.chat.id} при выполнении метода receive_video(): {err}")

    def log(self, message_text: str | None, message_chat_id: int, bot_reaction: str | None) -> None:
        try:
            filename = f"./logs/user_{message_chat_id}.json"
            cur_dialog = []
            if message_text:
                cur_dialog.append({
                    "role": "user",
                    "content": message_text,
                })
            if bot_reaction:
                cur_dialog.append({
                    "role": "assistant",
                    "content": bot_reaction
                })
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
                                  f"Ошибка у пользователя {message_chat_id} при выполнении метода log(): {err}")

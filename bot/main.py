from argparse import ArgumentParser
from data.classes import VideoHoster
from data.db_session import global_init
from os import getenv
from dotenv import load_dotenv
from telebot import TeleBot


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-l", "--log", action="store_true")
    args = parser.parse_args()
    load_dotenv()
    path_to_db = "../db/VideoHoster.db"
    global_init(path_to_db)
    bot = VideoHoster(TeleBot(getenv("TOKEN")), do_log=args.log, hoster=getenv("HOSTER"), path_to_db=path_to_db)

    @bot.bot.message_handler(commands=["start"])
    def greet(message):
        bot.greet(message)

    bot.bot.polling(non_stop=True)


if __name__ == "__main__":
    main()

from argparse import ArgumentParser
from data.classes import MyBot
from os import getenv
from dotenv import load_dotenv
from telebot import TeleBot


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-l", "--log", action="store_true")
    args = parser.parse_args()
    load_dotenv()
    bot = MyBot(TeleBot(getenv("TOKEN")), do_log=args.log, hoster=getenv("HOSTER"))

    @bot.bot.message_handler(commands=["start"])
    def greet(message):
        bot.greet(message)

    bot.bot.polling(non_stop=True)


if __name__ == "__main__":
    main()

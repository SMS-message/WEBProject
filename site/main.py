import sqlite3

from flask import Flask, render_template


def main() -> None:
    app = Flask(__name__)

    @app.route("/")
    @app.route("/index")
    def root() -> str:
        n = len(tuple(sqlite3.connect("../bot/db/VideoHoster.db").cursor().execute("SELECT ID FROM Videos;")))

        return render_template("index.html", number_of_videos=n)
    app.run(port=1501, host="127.0.0.1")


if __name__ == '__main__':
    main()

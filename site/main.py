import sqlite3

from flask import Flask, render_template
import os


def main() -> None:
    app = Flask(__name__)

    @app.route("/")
    @app.route("/index")
    def index() -> str:
        n = len(tuple(sqlite3.connect("../bot/db/VideoHoster.db").cursor().execute("SELECT ID FROM Videos;")))

        return render_template("index.html", number_of_videos=n, title="Video Hoster")

    @app.route("/about")
    def about():
        return render_template("about.html", title="О проекте")

    @app.route("/authors")
    def authors():
        return render_template("authors.html", title="Авторы")

    port = int(os.environ.get("PORT", 1501))
    app.run(port=port, host="0.0.0.0")


if __name__ == '__main__':
    main()

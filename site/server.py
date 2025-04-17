from flask import Flask, render_template
from flask_restful import Api
from data.video_resources import VideosResource, VideosListResource, Videos
from data.db_session import global_init, create_session
import os


def main() -> None:
    app = Flask(__name__)
    global_init("../db/VideoHoster.db")
    api = Api(app, catch_all_404s=True)

    @app.route("/")
    @app.route("/index")
    def index() -> str:
        n = len(create_session().query(Videos).all())

        return render_template("index.html", number_of_videos=n, title="Video Hoster")

    @app.route("/about")
    def about():
        return render_template("about.html", title="О проекте")

    @app.route("/authors")
    def authors():
        return render_template("authors.html", title="Авторы")

    api.add_resource(VideosResource, "/api/videos/<int:video_id>")
    api.add_resource(VideosListResource, "/api/videos")

    port = int(os.environ.get("PORT", 1501))
    app.run(port=port, host="0.0.0.0")


if __name__ == '__main__':
    main()

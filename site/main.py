from flask import Flask


def main() -> None:
    app = Flask(__name__)

    @app.route("/")
    def root() -> str:
        with open("index.html", mode="r", encoding="utf-8") as html:
            return html.read()

    app.run(port=1501, host="127.0.0.1")


if __name__ == '__main__':
    main()

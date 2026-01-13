from flask import Flask

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "Hello World Service running on datatailr!\n"


@app.route("/__health_check__.html", methods=["GET"])
def health_check():
    return "OK\n"


def main(port):
    app.run("0.0.0.0", port=int(port), debug=False)


if __name__ == "__main__":
    main(1024)

from flask import Flask

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return "pong"

app.run(host="0.0.0.0", port=56380)

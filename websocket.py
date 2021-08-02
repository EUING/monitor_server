from app import create_app
from flask_sock import Sock
import time

app = create_app()
sock = Sock(app)

@sock.route("/")
def reverse(ws):
    while True:
        time.sleep(5)
        ws.send("test")
from app import create_app
from flask import request
from flask_sock import Sock
from simple_websocket import ConnectionClosed
import json
import concurrent.futures

app = create_app()
sock = Sock(app)
app.client_list = dict()

def send(iter, data):
    return iter.send(data)    

def broadcast(ip, data):
    delete_list = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_broadcast = {executor.submit(send, v, data): k for k, v in app.client_list.items() if k != ip}
        for future in concurrent.futures.as_completed(future_broadcast):
            k = future_broadcast[future]
            if not future.result():
                delete_list.add(k)

    for ip in delete_list:
        app.client_list.pop(ip, -1)

app.broadcast = broadcast

class MyClient:
    def __init__(self, ws):
        self.ws = ws
        pass

    def receive(self):
        ret = True
        data = None
        try:
            data = self.ws.receive()
        except ConnectionClosed:
            ret = False
        return ret, data

    def send(self, data):
        ret = True
        try:
            self.ws.send(data)
        except ConnectionClosed:
            ret = False
        return ret

@sock.route("/")
def connect(ws):
    client = MyClient(ws)
    if not client.send(json.dumps({"event":"connected"})):
        print("connection failed")

    ip = client.ws.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    app.client_list[ip] = client
    print(ip + " connected")
    ret, message = client.receive()
    print(ip + " disconnected")
    app.client_list.pop(ip, -1)
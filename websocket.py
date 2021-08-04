from app import create_app
from flask_sock import Sock
from simple_websocket import ConnectionClosed
import json
import concurrent.futures

app = create_app()
sock = Sock(app)
app.client_list = set()

def send(iter, data):
    return iter.send(data)    

def broadcast(data):
    delete_list = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_broadcast = {executor.submit(send, iter, data): iter for iter in app.client_list}
        for future in concurrent.futures.as_completed(future_broadcast):
            iter = future_broadcast[future]
            if not future.result():
                delete_list.add(iter)

    for iter in delete_list:
        app.client_list.discard(iter)

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
    
    app.client_list.add(client)
    print("Client connected")
    ret, message = client.receive()
    print("Client disconnected")
    app.client_list.discard(client)
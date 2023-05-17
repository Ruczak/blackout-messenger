import json
from threading import Thread
from websockets.sync.server import serve, ServerConnection
from queue import LifoQueue
from datetime import datetime
from communication import Communication
from models.message import Message

device_identifier: str = "Block1"
radio_address = 0

radio_module = Communication('/dev/ttyS0', 433, radio_address)
connected = set()
radio_send_queue: LifoQueue[str] = LifoQueue()


def ws_handler(websocket: ServerConnection):
    connected.add(websocket)
    print(f"Websocket connected. Total websockets: {len(connected)}")
    try:
        for message in websocket:
            data = message if isinstance(message, str) else message.decode("utf-8")

            radio_send_queue.put(data)
    finally:
        connected.remove(websocket)
        print(f"Websocket disconnected. Total websockets: {len(connected)}")


def send_to_all(message: Message):
    sender_time = str(datetime.fromtimestamp(message.sender_time))
    data = {
        "address": message.address,
        "content": message.content,
        "sender_time": sender_time,
        "sender": message.sender,
    }
    json_data = json.dumps(data)

    for conn in connected:
        conn.send(json_data)


def radio_thread():
    print(f"Started receiving at address {radio_module.lora.addr}")
    while True:
        # sending data
        if not radio_send_queue.empty():
            item = radio_send_queue.get()
            m = radio_module.send(item)
            send_to_all(m)
            print(f"Sent data on address {radio_module.lora.addr}: {m.content}")
            radio_send_queue.task_done()

        # receiving data
        message = radio_module.receive()
        if message is not None:
            print(f"Received message \"{message.content}\" from {message.sender}")
            send_to_all(message)


def websocket_thread():
    with serve(ws_handler, '', port=8080) as server:
        print("Websocket server started")
        server.serve_forever()


if __name__ == '__main__':
    ws_thread = Thread(target=websocket_thread)
    communication_thread = Thread(target=radio_thread)
    ws_thread.start()
    communication_thread.start()

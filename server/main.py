import os
import json
from datetime import datetime
from threading import Thread
from queue import LifoQueue
from dotenv import load_dotenv
from websockets.sync.server import serve, ServerConnection

from database import Database
from communication import Communication
from models.message import Message

load_dotenv()

database = Database(os.environ.get("DB_USER"), os.environ.get("DB_PWD"), os.environ.get("DB_NAME"))
radio_module = Communication('/dev/ttyS0', 433, int(os.environ.get("RADIO_ADDRESS")), os.environ.get("DEVICE_NAME"))
connected: set[ServerConnection] = set()
radio_send_queue: LifoQueue[str] = LifoQueue()


def send_previous_messages(websocket: ServerConnection):
    for message in database.get_all_messages():
        iso_time = str(datetime.fromtimestamp(message.time))
        data = {
            "content": message.content,
            "time": iso_time,
            "sender": message.sender,
        }
        json_data = json.dumps(data)

        websocket.send(json_data)


def ws_handler(websocket: ServerConnection):
    connected.add(websocket)
    print(f"Websocket connected. Total websockets: {len(connected)}")

    try:
        send_previous_messages(websocket)

        for message in websocket:
            data = message if isinstance(message, str) else message.decode("utf-8")

            radio_send_queue.put(data)
    except ConnectionError:
        connected.remove(websocket)
        print(f"Connection Error, websocket disconnected. Total websockets: {len(connected)}")
    finally:
        connected.remove(websocket)
        print(f"Websocket disconnected. Total websockets: {len(connected)}")


def send_to_all(message: Message):
    iso_time = str(datetime.fromtimestamp(message.time))
    data = {
        "content": message.content,
        "time": iso_time,
        "sender": message.sender,
    }
    json_data = json.dumps(data)

    for conn in connected:
        try:
            conn.send(json_data)
        except ConnectionError:
            connected.remove(conn)
            print(f"Connection Error, websocket disconnected. Total websockets: {len(connected)}")


def radio_thread():
    print(f"Started receiving at address {radio_module.lora.addr}")
    while True:
        # sending data
        if not radio_send_queue.empty():
            item = radio_send_queue.get()
            m = radio_module.send(item)
            database.create_message(m)
            send_to_all(m)
            print(f"Sent data on address {radio_module.lora.addr}: {m.content}")
            radio_send_queue.task_done()

        # receiving data
        message = radio_module.receive()
        if message is not None:
            print(f"Received message \"{message.content}\" from {message.sender}")
            database.create_message(message)
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

from websockets.server import serve, WebSocketServerProtocol
import json
import asyncio
from threading import Thread
from queue import LifoQueue
from datetime import datetime
from communication import Communication
from models.message import Message

comms = Communication('/dev/ttyS0', 433, 0)
connected = set()
receive_queue = LifoQueue()


async def echo(websocket: WebSocketServerProtocol, path):
    connected.add(websocket)
    print(f"Websocket connected. Total websockets: {len(connected)}")
    try:
        async for message in websocket:
            data = message if isinstance(message, str) else message.decode("utf-8")
            # await websocket.send(data)
            print(f"Message {data}")
            m = await comms.send(22, data)
            await send_to_all(m)
    finally:
        connected.remove(websocket)


async def send_to_all(message: Message):
    date = str(datetime.fromtimestamp(message.sender_time))
    data = {
        "content": message.content,
        "time": date,
        "sender": "Block1"
    }
    json_data = json.dumps(data)
    for conn in connected:
        await conn.send(json_data)


async def check_queue():
    while not receive_queue.empty():
        message = receive_queue.get()
        await send_to_all(message)


def receive_infinitely():
    print(f"Started receiving at address {comms.lora.addr}")
    while True:
        message = comms.receive()
        if message != None:
            print(f"Received message \"{message.content}\" from {message.sender}")
            receive_queue.put(message)


async def main():
    try:
        async with serve(echo, port=8080):
            print("Websocket started")
            await asyncio.Future()
    except asyncio.CancelledError:
        print("Program stopped")


receive_thread = Thread(target=receive_infinitely)
receive_thread.start()
asyncio.run(main())

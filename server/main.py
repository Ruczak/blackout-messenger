from websockets.server import serve, WebSocketServerProtocol
import json
from datetime import datetime
import asyncio
from communication import Communication
from models.message import Message


comms = Communication('/dev/ttyS0', 433, 0)
connected = set()


async def echo(websocket, path):
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


async def callback(message: Message):
    print(f"Received message \"{message.content}\" from {message.sender}")
    await send_to_all(message)


async def receive_infinitely():
    try:
        print(f"Started receiving at address {comms.lora.addr}")
        while True:
            await comms.receive(callback)
    except asyncio.CancelledError:
        print("Stopped receiving")


async def main():
    try:
        async with serve(echo, port=8080):
            print("Websocket started")
            await asyncio.Future()
    except asyncio.CancelledError:
        print("Program stopped")


asyncio.run(main())
asyncio.run(receive_infinitely())

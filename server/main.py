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
    await send_to_all(message)


async def main():
    async with serve(echo, port=8080):
        print("Websocket started")
        await asyncio.Future()
        while True:
            await comms.receive(callback)


asyncio.run(main())

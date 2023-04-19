import json
import datetime
import asyncio
from queue import LifoQueue
from communication import Communication

comms = Communication(433, 0)

receive_queue = LifoQueue()
send_queue = LifoQueue()

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)
        await send(22, message)

async def receive_handler(addr, message):
    try:
        # print(f"Received buffer \"{message}\" from address {addr}")

    except asyncio.CancelledError:
        raise

async def main():
    async with serve(echo, port=8080):
        try:
            while True:
                await comms.receive(receive_handler)
        except asyncio.CancelledError:
            raise


asyncio.run(main())

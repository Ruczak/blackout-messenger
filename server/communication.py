import asyncio
from lora.sx126x import sx126x
import struct


class Communication(sx126x):
    def __init__(self, freq: int, address: int):
        sx126x.__init__(self, serial_num="/dev/ttyS0", freq=freq, addr=address, power=22, rssi=False, air_speed=2400, relay=False)

    # send row in specified format by frequency to address
    async def send(self, address: int, message: str):
        try:
            offset_frequency = int(freq) - (850 if int(freq) > 850 else 410)
            buffer = bytes(message, "utf-8")
            data = bytes([int(address) >> 8]) + bytes([int(address) & 0xff]) + bytes([offset_frequency]) + bytes([self.addr >> 8]) + bytes([self.addr & 0xff]) + bytes([self.offset_freq]) + buffer

            sx126x.send(self, data)
            print(f"Sent data to {address} / {freq} MHz: {buffer.hex()}")
        except asyncio.CancelledError:
            print("Cancelled sending data.")
            raise

    # receive information from other device and execute handler
    # with address and message passed
    async def receive(self, handler):
        try:
            if self.ser.inWaiting() > 0:
                await asyncio.sleep(0.5)
                r_buff = self.ser.read(self.ser.inWaiting())
                message = r_buff[6:].decode("utf-8")
                address = int(r_buff[4])
                handler(address, message)
        except asyncio.CancelledError:
            print("Cancelled receiving data")
            raise

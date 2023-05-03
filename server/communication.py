import time
import struct
from lora.sx126x import sx126x
from models.message import Message
from typing import Optional


class Communication:
    def __init__(self, serial_port: str, freq: int, address: int):
        self.lora = sx126x(serial_num=serial_port, freq=freq, addr=address, power=22, rssi=False, air_speed=2400,
                           relay=False)

    # send row in specified format by frequency to address
    def send(self, address: int, message: str) -> Message:
        m = Message(self.lora.addr, address, message, time.time())

        offset_frequency = int(self.lora.freq) - (850 if int(self.lora.freq) > 850 else 410)

        buffer = m.encode()
        data = bytes([int(address) >> 8]) + bytes([int(address) & 0xff]) + bytes([offset_frequency]) + bytes([
            self.lora.addr >> 8]) + bytes([self.lora.addr & 0xff]) + bytes([self.lora.offset_freq]) + buffer

        self.lora.send(data)

        return m

    # receive information from other device and execute handler
    # with address and message passed
    def receive(self) -> Optional[Message]:
        try:
            if self.lora.ser.inWaiting() > 0:
                time.sleep(0.5)
                r_buff = self.lora.ser.read(self.lora.ser.inWaiting())

                m = Message(int(r_buff[4]), self.lora.addr, r_buff[6:])
                return m
            return None
        except struct.error:
            print("An error occured!")
            return None

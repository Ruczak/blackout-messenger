import time
import struct


class Message:
    def __init__(self, sender: int, receiver: int, *args):
        self.sender = sender
        self.receiver = receiver

        if len(args) == 1 and isinstance(args[0], bytes):
            self.__decode()
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], float):
            self.message = args[0]
            self.sender_time = args[1]
        else:
            raise ValueError("Arguments passed to the constructor do not match")

    def __decode(self, buffer: bytes):
        self.sender_time = float(buffer[0:8])
        self.message = buffer[8:].decode("utf-8")

    def encode(self):
        s = bytes(self.message, "utf-8")
        return struct.pack("d%ds" % (len(s),), self.sender_time, s)

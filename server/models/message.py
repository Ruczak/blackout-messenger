import struct


class Message:
    def __init__(self, sender: int, receiver: int, *args):
        self.sender = sender
        self.receiver = receiver

        if len(args) == 1 and isinstance(args[0], bytes):
            self.__decode(args[0])
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], float):
            self.content = args[0]
            self.sender_time = args[1]
        else:
            raise ValueError("Arguments passed to the constructor do not match")

    def __decode(self, buffer: bytes):
        (self.sender_time, ), text_buffer = struct.unpack("d", buffer[:8]), buffer[8:]
        self.content = text_buffer.decode("utf-8")

    def encode(self):
        s = bytes(self.content, "utf-8")
        return struct.pack("d%ds" % (len(s),), self.sender_time, s)

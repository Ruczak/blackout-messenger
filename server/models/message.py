import struct
import time


class Message:
    def __init__(self, address: int, **kwargs):
        self.id: int = 0
        self.address = address

        if 'buffer' in kwargs and isinstance(kwargs['buffer'], bytes):
            self.__decode(kwargs['buffer'])
        elif 'sender' in kwargs and isinstance(kwargs['sender'], str) \
                and 'content' in kwargs and isinstance(kwargs['content'], str):
            self.sender = kwargs['sender']
            self.content = kwargs['content']
            if 'sender_time' in kwargs and isinstance(kwargs['sender_time'], float):
                self.sender_time = kwargs['sender_time']
            else:
                self.sender_time = time.time()
        else:
            raise ValueError("Arguments passed to the constructor do not match")

    def __decode(self, buffer: bytes):
        (self.sender_time, ), text_buffer = struct.unpack("d", buffer[:8]), buffer[8:]
        self.sender, self.content = text_buffer.decode("utf-8").split('\n')

    def encode(self) -> bytes:
        s = bytes(f"{self.sender}\n{self.content}", "utf-8")
        return struct.pack("d%ds" % (len(s),), self.sender_time, s)

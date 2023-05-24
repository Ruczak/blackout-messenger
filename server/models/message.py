import time


class Message:
    def __init__(self, **kwargs):
        self.id: int = 0
        self.time = time.time()

        if 'buffer' in kwargs and isinstance(kwargs['buffer'], bytes):
            self.__decode(kwargs['buffer'])
        elif 'sender' in kwargs and isinstance(kwargs['sender'], str) \
                and 'content' in kwargs and isinstance(kwargs['content'], str):
            self.sender = kwargs['sender']
            self.content = kwargs['content']

        else:
            raise ValueError("Arguments passed to the constructor do not match")

    def __decode(self, buffer: bytes):
        self.sender, self.content = buffer.decode("utf-8").split('\n')

    def encode(self) -> bytes:
        s = bytes(f"{self.sender}\n{self.content}", "utf-8")
        print(s)
        return s

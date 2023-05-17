import mariadb
import sys
from datetime import datetime
from typing import Optional

from models.message import Message


class Database:
    def __init__(self, user: str, password: str, db_name: str):
        try:
            self.connection = mariadb.connect(
                host="127.0.0.1",
                port=3306,
                user=user,
                password=password,
                database=db_name
            )

            self.cursor = self.connection.cursor()
        except mariadb.Error as e:
            print(f"Error connecting to the database: {e}")
            sys.exit(1)

    def __del__(self):
        self.close_connection()

    def close_connection(self):
        self.connection.close()
        print("Connection closed")

    def get_message(self, message_id: int) -> Optional[Message]:
        self.cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))

        for (db_id, sender, content, sender_time, address) in self.cursor:
            m = Message(address, sender=sender, content=content, sender_time=sender_time)
            m.id = db_id
            return m

        return None

    def get_all_messages(self) -> tuple[Message]:
        result: list[Message] = []

        self.cursor.execute("SELECT * FROM messages")

        for (db_id, sender, content, sender_time, address) in self.cursor:
            m = Message(address, sender=sender, content=content, sender_time=sender_time)
            m.id = db_id
            result.append(m)

        #print(result[0])

        return tuple(result)

    def create_message(self, message: Message):
        if message.id == 0:
            try:
                self.cursor.execute("INSERT INTO messages (sender, content, address, sender_time) "
                                    "VALUES (?, ?, ?, ?)",
                                    (message.sender, message.content, message.address,
                                    datetime.fromtimestamp(message.sender_time).strftime("%Y-%m-%d %H:%M:%S")))
                message.id = self.cursor.lastrowid

            except mariadb.Error as e:
                print(f"Error while inserting into the database {e}")

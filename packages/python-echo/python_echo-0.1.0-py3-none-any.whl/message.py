from datetime import datetime
from uuid import uuid4


class Message:
    def __init__(self, text: str, author: str):
        self.text = text
        self.author = author
        self.uid = uuid4().hex
        self.date = datetime.now()

    @staticmethod
    def random():
        return Message(text=uuid4().hex, author=uuid4().hex)

    def __str__(self):
        return f'Message {self.uid} by {self.author} created {self.date.strftime("%d.%m.%Y %H:%M:%S")}'

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        return {'text': self.text, 'author': self.author, 'uid': self.uid, 'date': self.date.strftime('%d.%m.%Y %H:%M:%S')}

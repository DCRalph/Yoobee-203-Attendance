import uuid

class Teacher:
    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name: str = name
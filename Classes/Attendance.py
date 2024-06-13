import uuid


class Attendance:
    def __init__(self, day: str):
        self.id = uuid.uuid4()
        self.day = day
        self.code = None

    def mark(self, code):
        self.code = code

    def display(self):
        print(f"Day: {self.day}, Code: {self.code}")

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            return NotImplemented
        return self.id == o.id

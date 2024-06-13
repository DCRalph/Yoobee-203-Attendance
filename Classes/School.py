import uuid
from Classes.Room import Room

class School:
    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name: str = name
        self.rooms: Room = []

    def add_room(self, room: Room):
        self.rooms.append(room)

    def display(self):
        for room in self.rooms:
            print("##################")
            print(f"Room: {room.name}")
            print(f"Teachers: ({len(room.teachers)})")
            for teacher in room.teachers:
                print(f"  - {teacher.name}")
            print(f"Students: ({len(room.students)})")
            for student in room.students:
                print(f"  - {student.first_name} {student.last_name}")
            print("##################")
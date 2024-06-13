
import uuid
from Classes.Attendance import Attendance

class Student:
    def __init__(self, first_name, last_name, date_of_birth):
        self.id = uuid.uuid4()
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.date_of_birth: str = date_of_birth
        self.attendances: set[Attendance] = set()

    def mark_attendance(self, day):
        attendance = Attendance(day)
        attendance.mark("P")
        self.attendances.add(attendance)
        return attendance

    def get_attendance(self, day):
        for attendance in self.attendances:
            if attendance.day == day:
                return attendance
        return None
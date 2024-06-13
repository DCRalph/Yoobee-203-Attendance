import uuid


class Room:
    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name: str = name
        # self.schoolId = school.id
        self.teachers = []
        self.students = []

    def add_teacher(self, teacher):
        self.teachers.append(teacher)

    def add_student(self, student):
        self.students.append(student)

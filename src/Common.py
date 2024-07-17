class Common:
#   pass
    class PicturesSchema:
        embedding = 0
        id = 1
        b64Img = 2
        studentId = 3
        distance = 4

    class UsersSchema:
        id = 0
        firstName = 1
        lastName = 2
    
    class StudentsSchema:
        id = 0
        first_name = 1
        last_name = 2
        date_of_birth = 3
        gender = 4
        class_room = 5

    class TeachersSchema:
        id = 0
        first_name = 1
        last_name = 2
        class_room = 3
        password = 4

    class StudentAttendanceSchema:
        id = 0
        student_id = 1
        date = 2
        code = 3
        entry_time = 4
        exit_time = 5

    class AttendanceCodes:
        present = 'P'
        absent = 'A'
        late = 'L'
        justified = 'J'


        

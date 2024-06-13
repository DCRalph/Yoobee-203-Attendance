import uuid
import tkinter as tk
import cv2
from PIL import Image, ImageTk

import webcamView


import Classes.Attendance
import Classes.Student
import Classes.Teacher
import Classes.Room
import Classes.School

window = tk.Tk()
window.title("Attendance System")
window.bind("<Escape>", lambda e: window.quit())

window.geometry("800x600")

cap = cv2.VideoCapture(0)


width, height = 800, 600
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


today = "2024-5-01"


school = Classes.School.School("School 1")
room = Classes.Room.Room("Room 1")
school.add_room(room)

teacher = Classes.Teacher.Teacher("Jane Doe")
room.add_teacher(teacher)

student = Classes.Student.Student("John", "Doe", "2000-01-01")
room.add_student(student)

student.mark_attendance(today)

school.display()

att = student.get_attendance(today)
# print(att)
att.display()


# label_widget = tk.Label(window)
# label_widget.pack()

# open and close button for webcamView

myWebcamView = webcamView.WebcamView(window)


toggle_button = tk.Button(window, text="Toggle Camera", command=myWebcamView.toggle_camera)
toggle_button.pack()

close_button = tk.Button(window, text="Close Camera", command=myWebcamView.close_camera)
close_button.pack()



window.mainloop()

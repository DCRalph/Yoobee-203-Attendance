import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel
from PIL import ImageTk
import psycopg2
from imgbeddings import imgbeddings
from Secrets import Secrets
import uuid

from Common import Common
import HandleImages
from Screens.ManageStudent import ManageStudent

db_connection = psycopg2.connect(Secrets.PG_URI)


# search user by name
# show list of users with there names and pictures
class TeacherManageClass:
    def __init__(self, root, class_room):
        self.root = root
        self.class_room = class_room

        self.window = Toplevel(root)
        self.window.title("Manage Class " + str(class_room))
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.students_array = []

        self.students_listbox = tk.Listbox(self.window)
        self.students_listbox.grid(row=0, column=0)

        self.students_listbox.bind("<Double-Button-1>", self.on_student_selected)

        self.load_students()

    def load_students(self):
        cur = db_connection.cursor()
        cur.execute(
            'SELECT * FROM "students" WHERE "class_room" = %s', (self.class_room,)
        )
        rows = cur.fetchall()

        self.students_array.clear()
        self.students_listbox.delete(0, tk.END)

        for i in range(len(rows)):
            student = rows[i]
            self.students_array.append(student)

            listboxStr = f"{i+1}. {student[Common.StudentsSchema.first_name]} {student[Common.StudentsSchema.last_name]}"
            self.students_listbox.insert(tk.END, listboxStr)

    def on_student_selected(self, event):

        selected_student_index = self.students_listbox.curselection()[0]
        selected_student = self.students_array[selected_student_index]

        ManageStudent(self.window, selected_student[Common.StudentsSchema.id])

    def on_closing(self):
        self.window.destroy()
        self.root.deiconify()

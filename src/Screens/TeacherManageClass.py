import tkinter as tk
from tkinter import messagebox, Toplevel
from PIL import ImageTk
import psycopg2
from imgbeddings import imgbeddings
from Secrets import Secrets
import uuid

from Common import Common
import HandleImages
from Screens.ManageStudent import ManageStudent

db_connection = psycopg2.connect(Secrets.PG_URI)

class TeacherManageClass:
    def __init__(self, root, class_room):
        self.root = root
        self.class_room = class_room

        self.window = Toplevel(root)
        self.window.title("Manage Class " + str(class_room))
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.students_array = []

        # Listbox to show the list of students
        self.students_listbox = tk.Listbox(self.window)
        self.students_listbox.grid(row=0, column=0, rowspan=6)

        self.students_listbox.bind("<Double-Button-1>", self.on_student_selected)

        # Labels and entries to show student details
        self.lbl_first_name = tk.Label(self.window, text="First Name:")
        self.lbl_first_name.grid(row=0, column=1)
        self.ent_first_name = tk.Entry(self.window)
        self.ent_first_name.grid(row=0, column=2)

        self.lbl_last_name = tk.Label(self.window, text="Last Name:")
        self.lbl_last_name.grid(row=1, column=1)
        self.ent_last_name = tk.Entry(self.window)
        self.ent_last_name.grid(row=1, column=2)

        self.lbl_student_id = tk.Label(self.window, text="Student ID:")
        self.lbl_student_id.grid(row=2, column=1)
        self.ent_student_id = tk.Entry(self.window)
        self.ent_student_id.grid(row=2, column=2)

        self.lbl_class_room = tk.Label(self.window, text="Class Room:")
        self.lbl_class_room.grid(row=3, column=1)
        self.ent_class_room = tk.Entry(self.window)
        self.ent_class_room.grid(row=3, column=2)

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

        # Update the details section with the selected student's information
        self.ent_first_name.delete(0, tk.END)
        self.ent_first_name.insert(0, selected_student[Common.StudentsSchema.first_name])
        
        self.ent_last_name.delete(0, tk.END)
        self.ent_last_name.insert(0, selected_student[Common.StudentsSchema.last_name])
        
        self.ent_student_id.delete(0, tk.END)
        self.ent_student_id.insert(0, selected_student[Common.StudentsSchema.id])
        
        self.ent_class_room.delete(0, tk.END)
        self.ent_class_room.insert(0, selected_student[Common.StudentsSchema.class_room])

    def on_closing(self):
        self.window.destroy()
        self.root.deiconify()

# Example usage:
# root = tk.Tk()
# TeacherManageClass(root, class_room=1)
# root.mainloop()

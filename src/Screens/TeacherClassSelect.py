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
from Screens.TeacherManageClass import TeacherManageClass

db_connection = psycopg2.connect(Secrets.PG_URI)


# search user by name
# show list of users with there names and pictures
class TeacherClassSelect:
    def __init__(self, root, teacher):
        self.root = root
        self.teacher = teacher

        self.window = Toplevel(root)
        self.window.title(f"Teacher {teacher[Common.TeachersSchema.first_name]} {teacher[Common.TeachersSchema.last_name]}")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # open your class btn
        self.open_your_class_btn = tk.Button(
            self.window,
            text="Open Your Class",
            command=self.open_your_class,
            background="green",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.open_your_class_btn.grid(row=0, column=0)
        
        self.all_classes_label = tk.Label(self.window, text="All Classes (0):")
        self.all_classes_label.grid(row=1, column=0, columnspan=2)

        self.all_classes_listbox = tk.Listbox(self.window)
        self.all_classes_listbox.grid(row=2, column=0)

        self.all_classes_listbox.bind("<Double-Button-1>", self.on_class_selected)

        self.classes_array = []

        self.load_classes()

    def load_classes(self):
        cur = db_connection.cursor()
        cur.execute('SELECT "students"."class_room" FROM "students"')
        rows = cur.fetchall()

        self.classes_array.clear()
        self.all_classes_listbox.delete(0, tk.END)

        for i in range(len(rows)):
            row = rows[i]

            if row[0] in self.classes_array:
                continue

            self.classes_array.append(row[0])

            listBoxStr = f"{i+1}. {row[0]}"
            self.all_classes_listbox.insert(tk.END, listBoxStr)

        self.all_classes_label.config(text=f"All Classes ({len(self.classes_array)}):")

    def on_class_selected(self, event):
        index = self.all_classes_listbox.curselection()[0]
        class_room = self.classes_array[index]

        TeacherManageClass(self.root, class_room)

    def open_your_class(self):
        TeacherManageClass(self.root, self.teacher[Common.TeachersSchema.class_room])

    def on_closing(self):
        self.window.destroy()
        self.root.deiconify()

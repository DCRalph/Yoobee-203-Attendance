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
from Screens.ManageUser import ManageUser

db_connection = psycopg2.connect(Secrets.PG_URI)


# search user by name
# show list of users with there names and pictures
class SearchUser:
    def __init__(self, root):
        self.root = root

        self.window = Toplevel(root)
        self.window.title("Search Student")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.label = tk.Label(self.window, text="Enter First Name:")
        self.label.grid(row=0, column=0)

        self.first_name_entry = tk.Entry(self.window)
        self.first_name_entry.grid(row=0, column=1)

        self.search_button = tk.Button(
            self.window,
            text="Search",
            command=self.search,
            background="blue",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.search_button.grid(row=1, column=0, columnspan=2)

        self.results_label = tk.Label(self.window, text="Results:")
        self.results_label.grid(row=2, column=0, columnspan=2)

        self.userArray = []

        self.results_listbox = tk.Listbox(self.window)
        self.results_listbox.grid(row=3, column=0, columnspan=2)

        self.results_listbox.bind("<Double-Button-1>", self.on_user_selected)

    def search(self):
        first_name = self.first_name_entry.get()

        cur = db_connection.cursor()
        if first_name == "":
            cur.execute("SELECT * FROM students")
        else:
            cur.execute("SELECT * FROM students WHERE first_name = %s", (first_name,))
        students = cur.fetchall()

        self.results_listbox.delete(0, tk.END)

        self.userArray.clear()

        for i in range(len(students)):
            student = students[i]
            self.userArray.append(student)

            listBoxStr = f"{i+1}. {student[Common.StudentsSchema.first_name]} {student[Common.StudentsSchema.last_name]}"

            self.results_listbox.insert(tk.END, listBoxStr)

    def on_user_selected(self, event):

        selected_student = self.userArray[self.results_listbox.curselection()[0]]
        print(selected_student)
        user_id = selected_student[Common.StudentsSchema.id]

        ManageUser(self.root, user_id)

        

    def on_closing(self):
        self.window.destroy()

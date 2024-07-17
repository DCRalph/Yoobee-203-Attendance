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
from Screens.TeacherClassSelect import TeacherClassSelect

db_connection = psycopg2.connect(Secrets.PG_URI)


# search user by name
# show list of users with there names and pictures
class TeacherLogin:
    def __init__(self, root):
        self.root = root

        self.window = Toplevel(root)
        self.window.title("Teacher Login")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.first_name_label = tk.Label(self.window, text="First Name:")
        self.first_name_label.grid(row=0, column=0)

        self.first_name_entry = tk.Entry(self.window)
        self.first_name_entry.grid(row=0, column=1)

        self.last_name_label = tk.Label(self.window, text="Last Name:")
        self.last_name_label.grid(row=1, column=0)

        self.last_name_entry = tk.Entry(self.window)
        self.last_name_entry.grid(row=1, column=1)

        self.password_label = tk.Label(self.window, text="Password:")
        self.password_label.grid(row=2, column=0)

        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.grid(row=2, column=1)

        self.login_button = tk.Button(
            self.window,
            text="Login",
            command=self.login,
            background="green",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.login_button.grid(row=3, column=0, columnspan=2)

    def login(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        password = self.password_entry.get()

        cur = db_connection.cursor()
        cur.execute(
            "SELECT * FROM teachers WHERE first_name = %s AND last_name = %s AND password = %s",
            (first_name, last_name, password),
        )
        teacher = cur.fetchone()

        if teacher:
            self.window.destroy()
            TeacherClassSelect(self.root, teacher)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def on_closing(self):
        self.window.destroy()
        self.root.deiconify()

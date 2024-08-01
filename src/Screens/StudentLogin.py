import customtkinter as ctk

from tkinter import messagebox
import psycopg2
from Screens.StudentPortal import StudentPortal
from Secrets import Secrets

db_connection = psycopg2.connect(Secrets.PG_URI)

class StudentLogin:
    def __init__(self, root):
        self.root = root

        self.window = ctk.CTkToplevel(root)
        self.window.title("Student Login")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.first_name_label = ctk.CTkLabel(self.window, text="First Name:")
        self.first_name_label.grid(row=0, column=0, padx=5, pady=5)

        self.first_name_entry = ctk.CTkEntry(self.window)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.last_name_label = ctk.CTkLabel(self.window, text="Last Name:")
        self.last_name_label.grid(row=1, column=0, padx=5, pady=5)

        self.last_name_entry = ctk.CTkEntry(self.window)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5)

        self.password_label = ctk.CTkLabel(self.window, text="Password:")
        self.password_label.grid(row=2, column=0, padx=5, pady=5)

        self.password_entry = ctk.CTkEntry(self.window, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        # self.first_name_entry.insert(0, "w")
        # self.last_name_entry.insert(0, "w")
        # self.password_entry.insert(0, "w")

        self.login_button = ctk.CTkButton(
            self.window,
            text="Login",
            command=self.login,
            font=("Helvetica", 16),
        )
        self.login_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def login(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        password = self.password_entry.get()

        cur = db_connection.cursor()
        cur.execute(
            "SELECT * FROM students WHERE first_name = %s AND last_name = %s AND password = %s",
            (first_name, last_name, password),
        )
        student = cur.fetchone()

        if student:
            self.window.destroy()
            StudentPortal(self.root, student[0])
        else:
            messagebox.showerror("Error", "Invalid Credentials")

            self.first_name_entry.delete(0, "end")
            self.last_name_entry.delete(0, "end")
            self.password_entry.delete(0, "end")



    def on_closing(self):
        self.window.destroy()
        self.root.deiconify()

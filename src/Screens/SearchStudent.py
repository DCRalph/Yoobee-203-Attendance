import customtkinter as ctk
import psycopg2
from imgbeddings import imgbeddings
from Secrets import Secrets
import uuid

from Common import Common
import HandleImages
from Screens.ManageStudent import ManageStudent

db_connection = psycopg2.connect(Secrets.PG_URI)


class ScrollListBox(ctk.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = ctk.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, id, item):
        label = ctk.CTkLabel(self, text=item, compound="left", padx=5, anchor="w")
        button = ctk.CTkButton(self, text="Manage", width=100, height=24)
        if self.command is not None:
            button.configure(command=lambda: self.command(id))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

    def remove_item(self, id, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return

    def remove_all_items(self):
        for label, button in zip(self.label_list, self.button_list):
            label.destroy()
            button.destroy()
        self.label_list.clear()
        self.button_list.clear()


class SearchStudent:
    def __init__(self, root):
        self.root = root

        self.window = ctk.CTkToplevel(root)
        self.window.title("Search Student")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.label = ctk.CTkLabel(self.window, text="Enter First Name:")
        self.label.grid(row=0, column=0, pady=5, padx=2)

        self.first_name_entry = ctk.CTkEntry(self.window)
        self.first_name_entry.grid(row=0, column=1)

        self.search_button = ctk.CTkButton(
            self.window,
            text="Search",
            command=self.search,
        )
        self.search_button.grid(row=1, column=0, columnspan=2, pady=5)

        self.results_label = ctk.CTkLabel(self.window, text="Results:")
        self.results_label.grid(row=2, column=0, columnspan=2, pady=5)

        self.results_listbox = ScrollListBox(
            self.window, command=self.on_user_selected, width=300
        )
        self.results_listbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def search(self):
        first_name = self.first_name_entry.get()

        cur = db_connection.cursor()
        if first_name == "":
            cur.execute("SELECT * FROM students")
        else:
            cur.execute("SELECT * FROM students WHERE first_name = %s", (first_name,))
        students = cur.fetchall()

        self.results_listbox.remove_all_items()

        for i in range(len(students)):
            student = students[i]
            listBoxStr = f"{i+1}. {student[Common.StudentsSchema.first_name]} {student[Common.StudentsSchema.last_name]}"

            self.results_listbox.add_item(student[Common.StudentsSchema.id], listBoxStr)

    def on_user_selected(self, item):
        ManageStudent(self.root, item)

    def on_closing(self):
        self.window.destroy()

import customtkinter as ctk

import psycopg2
from imgbeddings import imgbeddings
from Secrets import Secrets
import uuid

from Common import Common
import HandleImages
from Screens.TeacherManageClass import TeacherManageClass

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


class TeacherClassSelect:
    def __init__(self, root, teacher):
        self.root = root
        self.teacher = teacher

        self.window = ctk.CTkToplevel(root)
        self.window.title(
            f"Teacher {teacher[Common.TeachersSchema.first_name]} {teacher[Common.TeachersSchema.last_name]}"
        )
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # open your class btn
        self.open_your_class_btn = ctk.CTkButton(
            self.window,
            text="Open Your Class",
            command=self.open_your_class,
        )
        self.open_your_class_btn.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.all_classes_label = ctk.CTkLabel(self.window, text="All Classes (0):")
        self.all_classes_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.all_classes_listbox = ScrollListBox(
            self.window, command=self.on_class_selected, width=300
        )
        self.all_classes_listbox.grid(row=2, column=0, padx=10, pady=10)

        self.classes_array = []

        self.load_classes()

    def load_classes(self):
        cur = db_connection.cursor()
        cur.execute('SELECT "students"."class_room" FROM "students"')
        rows = cur.fetchall()

        self.classes_array.clear()

        for i in range(len(rows)):
            row = rows[i]

            if row[0] in self.classes_array:
                continue

            self.classes_array.append(row[0])

            listBoxStr = f"{i+1}. {row[0]}"
            self.all_classes_listbox.add_item(row[0], listBoxStr)

        self.all_classes_label.configure(
            text=f"All Classes ({len(self.classes_array)}):"
        )

    def on_class_selected(self, item):

        TeacherManageClass(self.root, item)

    def open_your_class(self):
        TeacherManageClass(self.root, self.teacher[Common.TeachersSchema.class_room])

    def on_closing(self):
        self.window.destroy()
        self.root.deiconify()

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
        button = ctk.CTkButton(self, text="Select", width=100, height=24)
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


class TeacherManageClass:
    def __init__(self, root, class_room):
        self.root = root
        self.class_room = class_room

        self.window = ctk.CTkToplevel(root)
        self.window.title("Manage Class " + str(class_room))
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.students_array = []
        self.selected_student = None

        # Listbox to show the list of students
        self.students_listbox = ScrollListBox(
            self.window, command=self.on_student_selected, width=300
        )
        self.students_listbox.grid(
            row=0, column=0, rowspan=10, columnspan=6, padx=10, pady=10
        )

        self.manage_student_button = ctk.CTkButton(
            self.window, text="Manage Student", command=self.manage_student
        )
        self.manage_student_button.grid(row=0, column=8, padx=5, pady=5)
        self.manage_student_button.configure(state="disabled")

        self.name_label = ctk.CTkLabel(self.window, text="Name:", anchor="w")
        self.name_label.grid(row=0, column=7, padx=5, pady=5)

        self.attendance_today_select = ctk.CTkOptionMenu(
            self.window,
            values=["Present", "Absent", "Late", "Justified"],
            command=self.on_attendance_today_selected,
        )
        self.attendance_today_select.grid(row=1, column=7, padx=5, pady=5)
        self.attendance_today_select.configure(state="disabled")

        self.next_student_button = ctk.CTkButton(
            self.window, text="Next Student", command=self.next_student
        )
        self.next_student_button.grid(row=6, column=7, padx=5, pady=5)

        # Labels and entries to show student details

        self.load_students()

    def load_students(self):
        cur = db_connection.cursor()
        cur.execute(
            'SELECT * FROM "students" WHERE "class_room" = %s', (self.class_room,)
        )
        rows = cur.fetchall()

        self.students_array.clear()
        self.students_listbox.remove_all_items()

        for i in range(len(rows)):
            student = rows[i]
            self.students_array.append(student)

            listboxStr = f"{i+1}. {student[Common.StudentsSchema.first_name]} {student[Common.StudentsSchema.last_name]}"
            self.students_listbox.add_item(i, listboxStr)

    def on_student_selected(self, item):
        self.selected_student = item
        print(self.students_array[self.selected_student])

        self.manage_student_button.configure(state="normal")
        self.attendance_today_select.configure(state="normal")

        self.name_label.configure(
            text=f"Name: {self.students_array[self.selected_student][Common.StudentsSchema.first_name]} {self.students_array[self.selected_student][Common.StudentsSchema.last_name]}"
        )
        
    def next_student(self):
        if self.selected_student is None:
            return

        self.selected_student += 1
        if self.selected_student >= len(self.students_array):
            self.selected_student = 0

        self.on_student_selected(self.selected_student)

    def on_attendance_today_selected(self, item):
        print(item)

    def manage_student(self):
        if self.selected_student is None:
            return

        ManageStudent(self.root, self.students_array[self.selected_student][Common.StudentsSchema.id])

    def on_closing(self):
        self.window.destroy()
        self.root.deiconify()


# Example usage:
# root = tk.Tk()
# TeacherManageClass(root, class_room=1)
# root.mainloop()

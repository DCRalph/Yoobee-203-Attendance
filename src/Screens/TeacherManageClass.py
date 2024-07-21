import datetime
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
        self.selected_student_saved = False

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

        self.attendance_label = ctk.CTkLabel(
            self.window, text="Attendance Today:", anchor="w"
        )
        self.attendance_label.grid(row=1, column=7, padx=5, pady=5)

        self.attendance_today_select = ctk.CTkOptionMenu(
            self.window,
            values=["N/A", Common.AttendanceCodes.present, Common.AttendanceCodes.absent, Common.AttendanceCodes.late, Common.AttendanceCodes.justified],
            command=self.on_attendance_today_selected,
        )
        self.attendance_today_select.grid(row=1, column=8, padx=5, pady=5)
        self.attendance_today_select.configure(state="disabled")

        self.entry_time_label = ctk.CTkLabel(
            self.window, text="Entry Time:", anchor="w"
        )
        self.entry_time_label.grid(row=2, column=7, padx=5, pady=5)

        self.entry_time_entry = ctk.CTkEntry(self.window)
        self.entry_time_entry.grid(row=2, column=8, padx=5, pady=5)
        self.entry_time_entry.configure(state="disabled")

        self.entry_time_now_btn = ctk.CTkButton(
            self.window, text="Now", command=self.entry_time_now
        )
        self.entry_time_now_btn.grid(row=2, column=9, padx=5, pady=5)
        self.entry_time_now_btn.configure(state="disabled")

        self.exit_time_label = ctk.CTkLabel(self.window, text="Exit Time:", anchor="w")
        self.exit_time_label.grid(row=3, column=7, padx=5, pady=5)

        self.exit_time_entry = ctk.CTkEntry(self.window)
        self.exit_time_entry.grid(row=3, column=8, padx=5, pady=5)
        self.exit_time_entry.configure(state="disabled")

        self.exit_time_now_btn = ctk.CTkButton(
            self.window, text="Now", command=self.exit_time_now
        )
        self.exit_time_now_btn.grid(row=3, column=9, padx=5, pady=5)
        self.exit_time_now_btn.configure(state="disabled")

        self.next_student_button = ctk.CTkButton(
            self.window, text="Next Student", command=self.next_student
        )
        self.next_student_button.grid(row=9, column=7, padx=5, pady=10)

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

        print(self.students_array)

    def on_student_selected(self, item):
        self.selected_student = item
        print(self.students_array[self.selected_student])

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        cur = db_connection.cursor()
        cur.execute(
            'SELECT * FROM "student_attendance" WHERE "studentId" = %s AND "date" = %s',
            (
                self.students_array[self.selected_student][Common.StudentsSchema.id],
                current_date,
            ),
        )
        attendance = cur.fetchone()

        self.manage_student_button.configure(state="normal")
        self.attendance_today_select.configure(state="normal")
        self.entry_time_entry.configure(state="normal")
        self.exit_time_entry.configure(state="normal")
        self.entry_time_now_btn.configure(state="normal")
        self.exit_time_now_btn.configure(state="normal")

        self.entry_time_entry.delete(0, "end")
        self.exit_time_entry.delete(0, "end")

        self.name_label.configure(
            text=f"Name: {self.students_array[self.selected_student][Common.StudentsSchema.first_name]} {self.students_array[self.selected_student][Common.StudentsSchema.last_name]}"
        )

        if attendance is None:
            self.attendance_today_select.set("N/A")
        else:
            self.attendance_today_select.set(attendance[Common.StudentAttendanceSchema.code])

            if attendance[Common.StudentAttendanceSchema.entry_time] is not None:
                self.entry_time_entry.insert(
                    0, attendance[Common.StudentAttendanceSchema.entry_time]
                )

            if attendance[Common.StudentAttendanceSchema.exit_time] is not None:
                self.exit_time_entry.insert(
                    0, attendance[Common.StudentAttendanceSchema.exit_time]
                )

    def on_attendance_today_selected(self, item):
        print(item)

    def entry_time_now(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.entry_time_entry.delete(0, "end")
        self.entry_time_entry.insert(0, current_time)

    def exit_time_now(self):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.exit_time_entry.delete(0, "end")
        self.exit_time_entry.insert(0, current_time)

    def next_student(self):
        if self.selected_student_saved is False and self.selected_student is not None:
            self.save()
            self.selected_student_saved = True

        if self.selected_student is None:
            if len(self.students_array) == 0:
                return
            self.selected_student = 0
            self.selected_student_saved = False

        else:
            self.selected_student += 1
            if self.selected_student >= len(self.students_array):
                self.selected_student = 0
                self.selected_student_saved = False

        self.on_student_selected(self.selected_student)

    def save(self):

        attendance_code = self.attendance_today_select.get()
        entry_time = self.entry_time_entry.get()
        exit_time = self.exit_time_entry.get()

        if entry_time == "":
            entry_time = None
        if exit_time == "":
            exit_time = None

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")

        cur = db_connection.cursor()
        cur.execute(
            'SELECT * FROM "student_attendance" WHERE "studentId" = %s AND "date" = %s',
            (
                self.students_array[self.selected_student][Common.StudentsSchema.id],
                current_date,
            ),
        )
        attendance = cur.fetchone()

        if attendance is None:
            cur.execute(
                'INSERT INTO "student_attendance" ("id", "studentId", "date", "code", "entry_time", "exit_time") VALUES (%s, %s, %s, %s, %s, %s)',
                (
                    uuid.uuid4(),
                    self.students_array[self.selected_student][
                        Common.StudentsSchema.id
                    ],
                    current_date,
                    attendance_code,
                    entry_time,
                    exit_time,
                ),
            )
        else:
            cur.execute(
                'UPDATE "student_attendance" SET "code" = %s, "entry_time" = %s, "exit_time" = %s WHERE "id" = %s',
                (
                    attendance_code,
                    entry_time,
                    exit_time,
                    attendance[Common.StudentAttendanceSchema.id],
                ),
            )

        db_connection.commit()

    def manage_student(self):
        if self.selected_student is None:
            return

        ManageStudent(
            self.root,
            self.students_array[self.selected_student][Common.StudentsSchema.id],
        )

    def on_closing(self):
        if self.selected_student_saved is False and self.selected_student is not None:
            self.save()
            self.selected_student_saved = True

        self.window.destroy()
        self.root.deiconify()


# Example usage:
# root = tk.Tk()
# TeacherManageClass(root, class_room=1)
# root.mainloop()

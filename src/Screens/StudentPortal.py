import datetime
import uuid
import customtkinter as ctk

from tkinter import messagebox
import psycopg2
import HandleImages
from Secrets import Secrets
from Common import Common


db_connection = psycopg2.connect(Secrets.PG_URI)

class StudentPortal:
    def __init__(self, root, studentId):
        self.root = root
        self.studentId = studentId

        self.window = ctk.CTkToplevel(root)
        self.window.title("Student Portal")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.label = ctk.CTkLabel(self.window, text="")
        self.label.grid(row=0, column=0, columnspan=2)

        self.welcome_label = ctk.CTkLabel(
            self.window, text="Welcome Student", font=("Helvetica", 16)
        )
        self.welcome_label.grid(row=1, column=0, columnspan=2)

        self.check_in_button = ctk.CTkButton(
            self.window,
            text="Check In",
            command=self.check_in,
            font=("Helvetica", 16),
        )
        self.check_in_button.grid(row=2, column=0, padx=5, pady=5)

        self.check_out_button = ctk.CTkButton(
            self.window,
            text="Check Out",
            command=self.check_out,
            font=("Helvetica", 16),
        )
        self.check_out_button.grid(row=2, column=1, padx=5, pady=5)

        self.images = None

        self.load_student()

    def load_student(self):
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM students WHERE id = %s", (self.studentId,))
        student = cur.fetchone()

        if student:
            self.welcome_label.configure(
                text=f"Welcome {student[Common.StudentsSchema.first_name]} {student[Common.StudentsSchema.last_name]}"
            )

            current_date = datetime.datetime.now().strftime("%d-%m-%Y")
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            cur.execute(
                'SELECT * FROM "student_attendance" WHERE "studentId" = %s AND "date" = %s',
                (
                    student[Common.StudentsSchema.id],
                    current_date,
                ),
            )

            attendance = cur.fetchone()

            if attendance:
                entry_time = attendance[Common.StudentAttendanceSchema.entry_time]
                exit_time = attendance[Common.StudentAttendanceSchema.exit_time]

                if entry_time != None and exit_time != None:
                    self.check_in_button.configure(state="disabled")
                    self.check_out_button.configure(state="disabled")
                elif entry_time != None and exit_time == None:
                    self.check_in_button.configure(state="disabled")
                    self.check_out_button.configure(state="normal")
                elif entry_time == None and exit_time != None:
                    self.check_in_button.configure(state="disabled")
                    self.check_out_button.configure(state="disabled")
                elif entry_time == None and exit_time == None:
                    self.check_in_button.configure(state="normal")
                    self.check_out_button.configure(state="disabled")
                else:
                    self.check_in_button.configure(state="disabled")
                    self.check_out_button.configure(state="disabled")
            else:
                self.check_in_button.configure(state="normal")
                self.check_out_button.configure(state="disabled")

            cur.execute(
                'SELECT * FROM pictures WHERE "studentId" = %s', (self.studentId,)
            )
            picture = cur.fetchone()

            if picture:
                image = HandleImages.get_image_from_cache(
                    picture[Common.PicturesSchema.id]
                )
                img = ctk.CTkImage(image, size=(200, 200))
                self.label.image = img
                self.label.configure(image=self.label.image)

    def check_in(self):
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        cur = db_connection.cursor()
        cur.execute(
                'INSERT INTO "student_attendance" ("id", "studentId", "date", "entry_time", "code") VALUES (%s, %s, %s, %s, %s)',
                (str(uuid.uuid4()), self.studentId, current_date, current_time, "Present"),
            )

        db_connection.commit()
        self.window.destroy()


    def check_out(self):
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        cur = db_connection.cursor()
        cur.execute(
            'SELECT * FROM "student_attendance" WHERE "studentId" = %s AND "date" = %s',
            (
                self.studentId,
                current_date,
            ),
        )

        attendance = cur.fetchone()

        if attendance:
            cur.execute(
                'UPDATE "student_attendance" SET "exit_time" = %s WHERE "id" = %s',
                (current_time, attendance[Common.StudentAttendanceSchema.id]),
            )

            db_connection.commit()
        else:
            messagebox.showerror("Error", "You have not checked in yet")
        
        self.window.destroy()

    def on_closing(self):
        self.window.destroy()
        self.root.deiconify()

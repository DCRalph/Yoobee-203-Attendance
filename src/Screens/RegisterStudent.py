import customtkinter as ctk
from tkinter import messagebox
from PIL import ImageTk
import psycopg2
from imgbeddings import imgbeddings
from Secrets import Secrets
import uuid

from Common import Common
import HandleImages

db_connection = psycopg2.connect(Secrets.PG_URI)


class RegisterStudent:
    def __init__(self, root, userImage):
        self.root = root
        self.userImage = userImage

        self.window = ctk.CTkToplevel(root)
        self.window.title("Register Student")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.ibed = imgbeddings()
        self.embedding = self.ibed.to_embeddings(self.userImage)

        self.label = ctk.CTkLabel(self.window, text="")

        self.imgtk = ImageTk.PhotoImage(image=self.userImage)

        self.label.configure(image=self.imgtk)
        self.label.grid(row=0, column=0, columnspan=2)

        # first name label
        self.first_name_label = ctk.CTkLabel(self.window, text="First Name:")
        self.first_name_label.grid(row=1, column=0, padx=5, pady=5)

        # first name entry
        self.first_name_entry = ctk.CTkEntry(self.window)
        self.first_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # last name label
        self.last_name_label = ctk.CTkLabel(self.window, text="Last Name:")
        self.last_name_label.grid(row=2, column=0, padx=5, pady=5)

        # last name entry
        self.last_name_entry = ctk.CTkEntry(self.window)
        self.last_name_entry.grid(row=2, column=1, padx=5, pady=5)

        # date of birth label
        self.date_of_birth_label = ctk.CTkLabel(self.window, text="Date of Birth:")
        self.date_of_birth_label.grid(row=3, column=0, padx=5, pady=5)

        # date of birth entry
        self.date_of_birth_entry = ctk.CTkEntry(self.window)
        self.date_of_birth_entry.grid(row=3, column=1, padx=5, pady=5)

        # gender label
        self.gender_label = ctk.CTkLabel(self.window, text="Gender:")
        self.gender_label.grid(row=4, column=0, padx=5, pady=5)

        # gender entry
        self.gender_entry = ctk.CTkEntry(self.window)
        self.gender_entry.grid(row=4, column=1, padx=5, pady=5)

        #class room label
        self.class_room_label = ctk.CTkLabel(self.window, text="Class Room(optional):")
        self.class_room_label.grid(row=5, column=0, padx=5, pady=5)

        #class room entry
        self.class_room_entry = ctk.CTkEntry(self.window)
        self.class_room_entry.grid(row=5, column=1, padx=5, pady=5)

        #password label
        self.password_label = ctk.CTkLabel(self.window, text="Password:")
        self.password_label.grid(row=6, column=0, padx=5, pady=5)

        #password entry
        self.password_entry = ctk.CTkEntry(self.window)
        self.password_entry.grid(row=6, column=1, padx=5, pady=5)

        # register button
        self.register_button = ctk.CTkButton(
            self.window,
            text="Register",
            command=self.register,
        )
        self.register_button.grid(row=7, column=0, padx=5, pady=5, columnspan=2)

    def register(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        date_of_birth = self.date_of_birth_entry.get()
        gender = self.gender_entry.get()
        class_room = self.class_room_entry.get()
        password = self.password_entry.get()

        print(f"Registering student: {first_name} {last_name}")

        # check if user already exists
        cur = db_connection.cursor()
        cur.execute(
            "SELECT * FROM students WHERE first_name = %s AND last_name = %s",
            (first_name, last_name),
        )

        studentId = None
        pictureId = str(uuid.uuid4())

        existing_student = cur.fetchone()

        if existing_student:
            print("Student already exists")
            studentId = existing_student[Common.StudentsSchema.id]

        else:
            studentId = str(uuid.uuid4())

            cur.execute(
                "INSERT INTO students VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (studentId, first_name, last_name, date_of_birth, gender, class_room, password),
            )

        b64Img = HandleImages.save_image_to_cache(self.userImage, pictureId)
        cur.execute(
            "INSERT INTO pictures VALUES (%s, %s, %s, %s)",
            (self.embedding[0].tolist(), pictureId, b64Img, studentId),
        )

        db_connection.commit()
        cur.close()

        if existing_student:
            messagebox.showinfo("Success", "Added picture to existing student")
        else:
            messagebox.showinfo("Success", "Student registered successfully")

        self.on_closing()

    def on_closing(self):
        self.window.destroy()

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

db_connection = psycopg2.connect(Secrets.PG_URI)


class ManageStudent:
    def __init__(self, root, studentId):
        self.root = root
        self.studentId = studentId

        self.window = Toplevel(root)
        self.window.title("Manage User")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.first_name_label = tk.Label(self.window, text="First Name:")
        self.first_name_label.grid(row=0, column=0)

        self.first_name_entry = tk.Entry(self.window)
        self.first_name_entry.grid(row=0, column=1)

        self.last_name_label = tk.Label(self.window, text="Last Name:")
        self.last_name_label.grid(row=0, column=2)

        self.last_name_entry = tk.Entry(self.window)
        self.last_name_entry.grid(row=0, column=3)

        self.date_of_birth_label = tk.Label(self.window, text="Date of Birth:")
        self.date_of_birth_label.grid(row=1, column=0)

        self.date_of_birth_entry = tk.Entry(self.window)
        self.date_of_birth_entry.grid(row=1, column=1)

        self.gender_label = tk.Label(self.window, text="Gender:")
        self.gender_label.grid(row=1, column=2)

        self.gender_entry = tk.Entry(self.window)
        self.gender_entry.grid(row=1, column=3)

        self.class_room_label = tk.Label(self.window, text="Class Room:")
        self.class_room_label.grid(row=2, column=0)

        self.class_room_entry = tk.Entry(self.window)
        self.class_room_entry.grid(row=2, column=1)

        self.update_button = tk.Button(
            self.window,
            text="Update",
            command=self.update,
            background="green",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.update_button.grid(row=3, column=0)

        self.delete_button = tk.Button(
            self.window,
            text="Delete",
            command=self.delete,
            background="red",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.delete_button.grid(row=3, column=1)

        # image casarousel with next and previous buttons and current image label

        self.next_button = tk.Button(
            self.window,
            text="Next",
            command=self.next_image,
            background="blue",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.next_button.grid(row=6, column=2)

        self.previous_button = tk.Button(
            self.window,
            text="Previous",
            command=self.previous_image,
            background="blue",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.previous_button.grid(row=6, column=0)

        self.current_image_label = tk.Label(self.window, text="Current Image: 0/0")
        self.current_image_label.grid(row=5, column=1)

        self.image_carousel = tk.Label(self.window)
        self.image_carousel.grid(row=6, column=1)

        self.images = []
        self.current_image = 0

        self.load_user()

    def load_user(self):
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM students WHERE id = %s", (self.studentId,))
        student = cur.fetchone()
        print(student)

        self.first_name_entry.insert(0, student[Common.StudentsSchema.first_name])
        self.last_name_entry.insert(0, student[Common.StudentsSchema.last_name])
        self.date_of_birth_entry.insert(0, student[Common.StudentsSchema.date_of_birth])
        self.gender_entry.insert(0, student[Common.StudentsSchema.gender])
        self.class_room_entry.insert(0, student[Common.StudentsSchema.class_room])

        cur.execute('SELECT * FROM pictures WHERE "studentId" = %s', (self.studentId,))
        pictures = cur.fetchall()

        self.images = []
        for picture in pictures:
            image = HandleImages.get_image_from_cache(picture[Common.PicturesSchema.id])
            self.images.append(image)

        self.update_image_carousel()

    def update_image_carousel(self):
        if len(self.images) == 0:
            self.image_carousel.configure(image="")
            return

        img = ImageTk.PhotoImage(self.images[self.current_image])
        self.image_carousel.configure(image=img)
        self.image_carousel.image = img

        self.current_image_label.configure(
            text=f"Current Image: {self.current_image + 1}/{len(self.images)}"
        )

    def next_image(self):
        self.current_image += 1
        if self.current_image >= len(self.images):
            self.current_image = 0

        self.update_image_carousel()

    def previous_image(self):
        self.current_image -= 1
        if self.current_image < 0:
            self.current_image = len(self.images) - 1

        self.update_image_carousel()

    def update(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        date_of_birth = self.date_of_birth_entry.get()
        gender = self.gender_entry.get()
        class_room = self.class_room_entry.get()

        cur = db_connection.cursor()
        cur.execute(
            "UPDATE students SET first_name = %s, last_name = %s, date_of_birth = %s, gender = %s, class_room = %s WHERE id = %s",
            (first_name, last_name, date_of_birth, gender, class_room, self.studentId),
        )

        db_connection.commit()

        messagebox.showinfo("Success", "User updated successfully")

        self.window.destroy()

    def delete(self):
        cur = db_connection.cursor()
        cur.execute('DELETE FROM pictures WHERE "studentId" = %s', (self.studentId,))
        cur.execute("DELETE FROM students WHERE id = %s", (self.studentId,))

        db_connection.commit()

        self.window.destroy()

    def on_closing(self):
        self.window.destroy()
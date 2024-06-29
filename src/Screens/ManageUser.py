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


class ManageUser:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id

        self.window = Toplevel(root)
        self.window.title("Manage User")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.label = tk.Label(self.window)
        self.label.grid(row=0, column=0, columnspan=2)

        self.first_name_label = tk.Label(self.window, text="First Name:")
        self.first_name_label.grid(row=1, column=0)

        self.first_name_entry = tk.Entry(self.window)
        self.first_name_entry.grid(row=1, column=1)

        self.last_name_label = tk.Label(self.window, text="Last Name:")
        self.last_name_label.grid(row=2, column=0)

        self.last_name_entry = tk.Entry(self.window)
        self.last_name_entry.grid(row=2, column=1)

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
        self.update_button.grid(row=3, column=0, columnspan=2)

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
        self.delete_button.grid(row=4, column=0, columnspan=2)

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
        self.next_button.grid(row=6, column=0)

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
        self.previous_button.grid(row=6, column=1)

        self.current_image_label = tk.Label(self.window, text="Current Image: 0/0")
        self.current_image_label.grid(row=5, column=0, columnspan=2)

        self.image_carousel = tk.Label(self.window)
        self.image_carousel.grid(row=6, column=0, columnspan=2)

        self.images = []
        self.current_image = 0

        self.load_user()

    def load_user(self):
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (self.user_id,))
        user = cur.fetchone()

        self.first_name_entry.insert(0, user[1])
        self.last_name_entry.insert(0, user[2])

        cur.execute('SELECT * FROM pictures WHERE "userId" = %s', (self.user_id,))
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

        self.current_image_label.configure(text=f"Current Image: {self.current_image + 1}/{len(self.images)}")

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

        cur = db_connection.cursor()
        cur.execute(
            "UPDATE users SET first_name = %s, last_name = %s WHERE id = %s",
            (first_name, last_name, self.user_id),
        )

        db_connection.commit()

        messagebox.showinfo("Success", "User updated successfully")

    def delete(self):
        cur = db_connection.cursor()
        cur.execute('DELETE FROM pictures WHERE "userId" = %s', (self.user_id,))
        cur.execute("DELETE FROM users WHERE id = %s", (self.user_id,))

        db_connection.commit()

        self.window.destroy()

    def on_closing(self):
        self.window.destroy()

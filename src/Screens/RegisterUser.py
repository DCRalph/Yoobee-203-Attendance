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


class RegisterUser:
    def __init__(self, root, userImage):
        self.root = root
        self.userImage = userImage

        self.window = Toplevel(root)
        self.window.title("Register User")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.ibed = imgbeddings()
        self.embedding = self.ibed.to_embeddings(self.userImage)

        self.label = tk.Label(self.window)

        self.imgtk = ImageTk.PhotoImage(image=self.userImage)

        self.label.configure(image=self.imgtk)
        self.label.grid(row=0, column=0, columnspan=2)

        # first name label
        self.first_name_label = tk.Label(self.window, text="First Name:")
        self.first_name_label.grid(row=1, column=0)

        # first name entry
        self.first_name_entry = tk.Entry(self.window)
        self.first_name_entry.grid(row=1, column=1)

        # last name label
        self.last_name_label = tk.Label(self.window, text="Last Name:")
        self.last_name_label.grid(row=2, column=0)

        # last name entry
        self.last_name_entry = tk.Entry(self.window)
        self.last_name_entry.grid(row=2, column=1)

        # register button
        self.register_button = tk.Button(
            self.window,
            text="Register",
            command=self.register,
            background="green",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.register_button.grid(row=3, column=0, columnspan=2)

    def register(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()

        print(f"Registering user: {first_name} {last_name}")

        # check if user already exists
        cur = db_connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE first_name = %s AND last_name = %s",
            (first_name, last_name),
        )

        userId = None
        pictureId = str(uuid.uuid4())

        existing_user = cur.fetchone()

        if existing_user:
            print("User already exists")
            userId = existing_user[Common.UsersSchema.id]

        else:

            userId = str(uuid.uuid4())

            cur.execute(
                "INSERT INTO users VALUES (%s, %s, %s)", (userId, first_name, last_name)
            )

        b64Img = HandleImages.save_image_to_cache(self.userImage, pictureId)
        cur.execute(
            "INSERT INTO pictures VALUES (%s, %s, %s, %s)",
            (self.embedding[0].tolist(), userId, pictureId, b64Img),
        )

        db_connection.commit()
        cur.close()

        if existing_user:
            messagebox.showinfo("Success", "Added picture to existing user")
        else:
            messagebox.showinfo("Success", "User registered successfully")

        self.on_closing()

    def on_closing(self):
        self.window.destroy()

import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel
import cv2
import threading
from PIL import Image, ImageTk
import psycopg2
from imgbeddings import imgbeddings
from Secrets import Secrets

from RegisterUser import RegisterUser


CAMERA_FPS = 60
CAMERA_FPS_MS = int(1000 / CAMERA_FPS)
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

FACE_DETECT_ALG_PATH = "vector2/haarcascade_frontalface_default.xml"
FACE_DETECT_ALG = cv2.CascadeClassifier(FACE_DETECT_ALG_PATH)

SAVED_PICTURES_PATH = "vector2/savedPictures"

db_connection = psycopg2.connect(Secrets.PG_URI)


class CameraFeed:
    def __init__(self, root):
        self.root = root

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

        self.frame = None

        self.running = False

        self.window = Toplevel(root)
        self.window.title("Live Camera Feed")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.label = tk.Label(self.window)
        self.label.grid(row=0, column=0, columnspan=2)

        # scan button
        self.scan_button = tk.Button(
            self.window,
            text="Scan",
            command=self.scan,
            background="green",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.scan_button.grid(row=1, column=0)

        # register user button
        self.register_user_button = tk.Button(
            self.window,
            text="Register User",
            command=self.register_user,
            background="blue",
            foreground="white",
            font=("Helvetica", 16),
            width=20,
            height=2,
        )
        self.register_user_button.grid(row=1, column=1)

        self.faces = []

        self.start_feed()

    def start_feed(self):
        self.running = True
        self.thread = threading.Thread(target=self.update_feed_gui_safe)
        self.thread.start()

    def update_feed_gui_safe(self):
        if self.running:
            ret, self.frame = self.cap.read()

            if ret:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                self.frame = cv2.resize(self.frame, (1280, 720))

                frameCopy = self.frame.copy()

                self.detect_faces()
                for x, y, w, h in self.faces:
                    cv2.rectangle(frameCopy, (x, y), (x + w, y + h), (255, 0, 0), 2)

                img = Image.fromarray(frameCopy)
                imgtk = ImageTk.PhotoImage(image=img)

                self.label.imgtk = imgtk  # Reference must be maintained
                self.label.configure(image=self.label.imgtk)

            else:
                print("Error reading frame")
            self.label.after(CAMERA_FPS_MS, self.update_feed_gui_safe)

    def detect_faces(self):
        gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_DETECT_ALG.detectMultiScale(
            self.frame, scaleFactor=1.05, minNeighbors=2, minSize=(100, 100)
        )
        self.faces = faces

    def scan(self):
        print("Scanning...")
        if len(self.faces) == 0:
            print("No faces detected")
            messagebox.showerror("Error", "No faces detected")
            return

        if len(self.faces) > 1:
            print("Multiple faces detected")
            messagebox.showerror("Error", "Multiple faces detected")
            return

        x, y, w, h = self.faces[0]
        img = Image.fromarray(self.frame)
        cropped_image = img.crop((x, y, x + w, y + h))

        img2 = cropped_image

        print("Scanning image...")

        ibed = imgbeddings()
        embedding = ibed.to_embeddings(img2)

        print("created embedding")

        string_representation = (
            "[" + ",".join(str(x) for x in embedding[0].tolist()) + "]"
        )

        # print(string_representation)

        cur = db_connection.cursor()
        cur.execute(
            "SELECT * FROM pictures ORDER BY embedding <-> %s LIMIT 1",
            (string_representation,),
        )

        rows = cur.fetchall()
        if len(rows) == 0:
            print("No match found")
            messagebox.showerror("Error", "No match found")
            return

        print(rows)
        cur.execute("SELECT * FROM users WHERE id = %s", (rows[0][1],))
        user = cur.fetchone()
        print(user)
        print(f"Match found: {user[1]} {user[2]}")
        messagebox.showinfo("Match Found", f"Match found: {user[1]} {user[2]}")

        cur.close()

    def register_user(self):
        if len(self.faces) == 0:
            print("No faces detected")
            messagebox.showerror("Error", "No faces detected")
            return

        if len(self.faces) > 1:
            print("Multiple faces detected")
            messagebox.showerror("Error", "Multiple faces detected")
            return

        # get the first face detected and crop the image
        x, y, w, h = self.faces[0]
        img = Image.fromarray(self.frame)
        cropped_image = img.crop((x, y, x + w, y + h))

        RegisterUser(self.root, cropped_image)

    def on_closing(self):
        self.running = False
        self.cap.release()
        self.window.destroy()

import datetime
import uuid
import customtkinter as ctk
from tkinter import messagebox
import cv2
import threading
from PIL import Image, ImageTk
import numpy as np
import psycopg2
from imgbeddings import imgbeddings
from Screens.StudentLogin import StudentLogin
from Secrets import Secrets
from Common import Common
import HandleImages

from Screens.RegisterStudent import RegisterStudent


CAMERA_FPS = 25
CAMERA_FPS_MS = int(1000 / CAMERA_FPS)
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# print(CAMERA_FPS_MS)

FACE_DETECT_ALG_PATH = "src/haarcascade_frontalface_default.xml"
FACE_DETECT_ALG = cv2.CascadeClassifier(FACE_DETECT_ALG_PATH)


db_connection = psycopg2.connect(Secrets.PG_URI)


class CameraFeed:
    def __init__(self, root, is_register=False):
        self.root = root
        self.is_register = is_register

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        self.frame = None

        self.running = False
        self.scanning = False

        self.window = ctk.CTkToplevel(root)
        self.window.title("Live Camera Feed")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.label = ctk.CTkLabel(self.window, text="")
        self.label.grid(row=0, column=0, columnspan=3)

        # self.canvas = tk.Canvas(self.window, width=1280, height=720)
        # self.canvas.grid(row=0, column=0, columnspan=2)

        # self.image_id = None

        if self.is_register:
            # register button
            self.register_button = ctk.CTkButton(
                self.window,
                text="Register",
                command=self.register_user,
                fg_color="green",
                height=100,
                width=400,
                font=("Arial", 20),
            )
            self.register_button.grid(row=1, column=1, padx=5, pady=5)
        else:
            # scan button
            self.scan_button = ctk.CTkButton(
                self.window,
                text="Scan",
                command=self.scan,
                fg_color="red",
                height=100,
                width=400,
                font=("Arial", 20),
            )
            self.scan_button.grid(row=1, column=1, padx=5, pady=5)

        # manuel login button
        self.manual_login_button = ctk.CTkButton(
            self.window,
            text="Manual Login",
            command=self.student_login,
            fg_color="blue",
            height=100,
            width=400,
            font=("Arial", 20),
        )
        self.manual_login_button.grid(row=1, column=0, padx=5, pady=5)

        self.faces = []

        self.start_feed()

    def start_feed(self):
        # self.running = True
        # self.thread = threading.Thread(target=self.update_feed_gui_safe)
        # self.thread.start()
        self.running = True
        self.update_feed_gui_safe()

    def update_feed_gui_safe(self):
        if self.running:
            ret, self.frame = self.cap.read()

            if ret:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                self.frame = cv2.resize(self.frame, (1280, 720))

                frameCopy = self.frame.copy()
                shapes = np.zeros_like(frameCopy, np.uint8)

                cv2.rectangle(shapes, (400, 50), (880, 100), (1, 1, 1), -1)
                mask = shapes.astype(bool)
                frameCopy[mask] = cv2.addWeighted(frameCopy, 0.5, shapes, 0.5, 0)[mask]

                # rectangle in center of screen with text "Face"
                cv2.rectangle(frameCopy, (400, 100), (880, 620), (0, 255, 0), 2)
                cv2.putText(
                    frameCopy,
                    "Face",
                    (600, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )
                cv2.putText(
                    frameCopy,
                    "Make sure your face is inside the rectangle",
                    (480, 92),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

                if self.scanning:
                    # black out the frame and mask the detected face and put scan text
                    detectedFaceMask = np.zeros_like(frameCopy, np.uint8)

                    x, y, w, h = self.faces[0]
                    cv2.rectangle(
                        detectedFaceMask, (x, y), (x + w, y + h), (255, 255, 255), -1
                    )
                    mask = detectedFaceMask.astype(bool)
                    frameCopy = cv2.bitwise_and(frameCopy, detectedFaceMask)

                    cv2.putText(
                        frameCopy,
                        "Scanning...",
                        (x, y - 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        2,
                    )

                    cv2.putText(
                        frameCopy,
                        "Please wait",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1,
                    )

                self.detect_faces()
                for x, y, w, h in self.faces:
                    cv2.rectangle(frameCopy, (x, y), (x + w, y + h), (255, 0, 0), 2)

                img = Image.fromarray(frameCopy)
                self.label.imgtk = ImageTk.PhotoImage(image=img)
                self.label.configure(image=self.label.imgtk)

            else:
                print("Error reading frame")
            self.label.after(15, self.update_feed_gui_safe)

    def detect_faces(self):
        if self.scanning:
            return
        gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_DETECT_ALG.detectMultiScale(
            self.frame, scaleFactor=1.05, minNeighbors=2, minSize=(100, 100)
        )
        self.faces = faces

    def scan(self):
        print("Scanning...")

        tmpFaces = []
        for x, y, w, h in self.faces:
            if x > 400 and y > 100 and x + w < 880 and y + h < 620:
                tmpFaces.append((x, y, w, h))
        self.faces = tmpFaces

        if len(self.faces) == 0:
            print("No faces detected")
            messagebox.showerror("Error", "No faces detected")
            return

        if len(self.faces) > 1:
            print("Multiple faces detected")
            messagebox.showerror("Error", "Multiple faces detected")
            return

        self.scanning = True
        self.label.after(1000, self.perform_scan)

    def perform_scan(self):
        self.scanning = False

        print(self.faces)
        x, y, w, h = self.faces[0]
        print(x, y, w, h)
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
            "SELECT *, (embedding <-> %s) AS distance FROM pictures ORDER BY distance LIMIT 1",
            (string_representation,),
        )

        picRes = cur.fetchone()

        if picRes is None:
            print("No match found")
            messagebox.showinfo("No Match Found", "No match found")
            return

        distance = picRes[Common.PicturesSchema.distance]

        if distance > 15:
            print("No match found")
            messagebox.showinfo("No Match Found", "No match found")
            return

        cur.execute(
            "SELECT * FROM students WHERE id = %s",
            (picRes[Common.PicturesSchema.studentId],),
        )
        student = cur.fetchone()
        print(student)
        print(
            f"Match found: {student[Common.StudentsSchema.first_name]} {student[Common.StudentsSchema.last_name]}"
        )

        cur.close()

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        cur = db_connection.cursor()
        cur.execute(
            'SELECT * FROM "student_attendance" WHERE "studentId" = %s AND "date" = %s',
            (
                student[Common.StudentsSchema.id],
                current_date,
            ),
        )

        attendance = cur.fetchone()

        msg_title = ""
        msg_body = ""

        # check if student has already been marked present and it was less than 5 minutes ago
        if attendance is not None:
            time_entered = datetime.datetime.strptime(
                attendance[Common.StudentAttendanceSchema.entry_time], "%H:%M:%S"
            )

            if attendance[Common.StudentAttendanceSchema.entry_time] is not None and attendance[Common.StudentAttendanceSchema.exit_time] is not None:
                print("Already marked present and exit")
                messagebox.showerror("Error", "Already marked present and exit")
                return

            if (datetime.datetime.now() - time_entered).seconds < 300:
                print("Already marked present")
                messagebox.showerror("Error", "Already marked present")
                return

            cur.execute(
                'UPDATE "student_attendance" SET "exit_time" = %s WHERE "studentId" = %s AND "date" = %s',
                (current_time, student[Common.StudentsSchema.id], current_date),
            )

            msg_title = "Marked Exit"
            msg_body = f"Marked exit for {student[Common.StudentsSchema.first_name]} {student[Common.StudentsSchema.last_name]}"

        else:
            cur.execute(
                'INSERT INTO "student_attendance" ("id", "studentId", "date", "entry_time", "code") VALUES (%s, %s, %s, %s, %s)',
                (str(uuid.uuid4()), student[Common.StudentsSchema.id], current_date, current_time, "Present"),
            )

            msg_title = "Marked Present"
            msg_body = f"Marked present for {student[Common.StudentsSchema.first_name]} {student[Common.StudentsSchema.last_name]}"

        db_connection.commit()

        messagebox.showinfo(msg_title, msg_body)

        cur.close()

    def register_user(self):
        print("Scanning...")

        tmpFaces = []
        for x, y, w, h in self.faces:
            if x > 400 and y > 100 and x + w < 880 and y + h < 620:
                tmpFaces.append((x, y, w, h))
        self.faces = tmpFaces

        if len(self.faces) == 0:
            print("No faces detected")
            messagebox.showerror("Error", "No faces detected")
            return

        if len(self.faces) > 1:
            print("Multiple faces detected")
            messagebox.showerror("Error", "Multiple faces detected")
            return

        self.scanning = True
        self.label.after(1000, self.process_register)

    def process_register(self):

        # get the first face detected and crop the image
        x, y, w, h = self.faces[0]
        img = Image.fromarray(self.frame)
        cropped_image = img.crop((x, y, x + w, y + h))

        RegisterStudent(self.root, cropped_image)

    def student_login(self):
        StudentLogin(self.root)

    def on_closing(self):
        self.running = False
        self.cap.release()
        self.window.destroy()

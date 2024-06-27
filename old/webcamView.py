import tkinter as tk
import cv2
from PIL import Image, ImageTk


class WebcamView(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.is_open = False

    # def init(self):
        

    # def create_widgets(self):
    #     self.label_widget = tk.Label(self)
    #     self.label_widget.pack()

    #     self.cap = cv2.VideoCapture(0)
    #     self.width, self.height = 800, 600
    #     self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
    #     self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def open_camera(self):
        self.pack()
        self.label_widget = tk.Label(self)
        self.label_widget.pack()

        self.cap = cv2.VideoCapture(0)
        self.width, self.height = 800, 600
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        _, frame = self.cap.read()

        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        photo_image = ImageTk.PhotoImage(image=img)

        self.label_widget.photo_image = photo_image
        self.label_widget.configure(image=photo_image)
        self.label_widget.after(10, self.open_camera)

        self.is_open = True

    def close_camera(self):
        self.pack_forget()
        self.label_widget.pack_forget()

        self.cap.release()
        self.is_open = False

    def toggle_camera(self):
        if self.is_open:
            self.close_camera()
        else:
            self.open_camera()

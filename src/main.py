import tkinter as tk

from Screens.CameraFeed import CameraFeed
from Screens.SearchStudent import SearchStudent
from Screens.TeacherLogin import TeacherLogin


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Main Window")
        self.geometry("200x100")

        self.button = tk.Button(
            self, text="Open Camera Feed", command=self.open_camera_feed
        )
        self.button.pack()

        # search user button
        self.button = tk.Button(self, text="Search User", command=self.search_user)
        self.button.pack()

        self.teacher_login_button = tk.Button(
            self, text="Teacher Login", command=self.teacher_login
        )
        self.teacher_login_button.pack()

        self.mainloop()

    def open_camera_feed(self):
        CameraFeed(self)

    def search_user(self):
        SearchStudent(self)

    def teacher_login(self):
        TeacherLogin(self)


if __name__ == "__main__":
    app = MainWindow()

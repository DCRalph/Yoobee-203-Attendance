import customtkinter as ctk

from Screens.CameraFeed import CameraFeed
from Screens.SearchStudent import SearchStudent
from Screens.TeacherLogin import TeacherLogin

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("School attendance system")
        self.geometry("200x150")

        self.button = ctk.CTkButton(
            self, text="Open Camera Feed", command=self.open_camera_feed
        )
        self.button.pack(pady=5)

        # search user button
        self.button = ctk.CTkButton(self, text="Search User", command=self.search_user)
        self.button.pack(pady=5)

        self.teacher_login_button = ctk.CTkButton(
            self, text="Teacher Login", command=self.teacher_login
        )
        self.teacher_login_button.pack(pady=5)

        self.mainloop()

    def open_camera_feed(self):
        CameraFeed(self)

    def search_user(self):
        SearchStudent(self)

    def teacher_login(self):
        TeacherLogin(self)


if __name__ == "__main__":
    app = MainWindow()

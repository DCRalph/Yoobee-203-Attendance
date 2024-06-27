import tkinter as tk

from Screens.CameraFeed import CameraFeed


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Main Window")
        self.geometry("200x100")

        self.button = tk.Button(
            self, text="Open Camera Feed", command=self.open_camera_feed
        )
        self.button.pack()

        self.mainloop()

    def open_camera_feed(self):
        CameraFeed(self)


if __name__ == "__main__":
    app = MainWindow()

import tkinter as tk

from CameraFeed import CameraFeed


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Window")
        self.root.geometry("200x100")

        self.button = tk.Button(
            root, text="Open Camera Feed", command=self.open_camera_feed
        )
        self.button.pack()

    def open_camera_feed(self):
        CameraFeed(self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

import os
import tkinter as tk
from tkinter import ttk
from time import sleep

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        label = ttk.Label(self, text="Connexion")
        label.pack(pady=10, padx=10)
        icon_path = os.path.join(os.path.dirname(__file__), 'logo.png')  # Ensure this is the correct path
        self.icon_image = tk.PhotoImage(file=icon_path)
        canvas = tk.Canvas(self, width=350, height=361)
        canvas.create_image(0, 0, anchor="nw", image=self.icon_image)
        canvas.pack()
        self.username = ttk.Entry(self)
        self.username.pack(pady=5, padx=10)
        self.username.insert(0, "Username")
        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5, padx=10)
        self.password.insert(0, "Password")
        self.login_button = ttk.Button(self, text="Login", command=self.login)
        self.login_button.pack(pady=5, padx=10)

    def login(self):
        self.controller.username = self.username.get()
        self.text= ttk.Label(self, text="Connexion en cours...")
        self.text.pack(pady=10, padx=10)
        self.controller.show_frame("RoomPage")
        self.controller.frames["RoomPage"].initialize_client()
        sleep(0.3)
        self.controller.frames["RoomPage"].actualise()
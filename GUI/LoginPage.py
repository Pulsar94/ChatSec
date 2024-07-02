import os
import tkinter as tk
from tkinter import ttk
from time import sleep
import threading
import socket

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.client = controller.client
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
        self.username.insert(0, "tibo@secu.hack") # for debugging

        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5, padx=10)
        self.password.insert(0, "1234")

        self.text= ttk.Label(self, text="")
        self.text.pack(pady=10, padx=10)

        self.login_button = ttk.Button(self, text="Login", command=self.login)
        self.login_button.pack(pady=5, padx=10)
    
    def update_text(self, text):
        self.text.config(text=text)

    def login(self):
        self.controller.username = self.username.get()
        self.update_text("Connexion in progress...")
        self.initialize_client(self.username.get(), self.password.get())
    
    def initialize_client(self, username, password):
        self.client.sv_connect(socket.gethostname(), 5000)
        threading.Thread(target=self.client.sv_listen).start()
        sleep(1)
        self.client.sv_authentification(username, password)
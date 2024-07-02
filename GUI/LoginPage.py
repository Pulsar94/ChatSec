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
        self.new_user = None
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

    def add_account(self):
        self.new_user = tk.Toplevel(self)
        self.new_user.title("Add User")
        self.new_user.geometry("300x200")  # Width x Height

        mail_label = ttk.Label(self.new_user, text="Enter your mail:")
        mail_label.pack(pady=10, padx=10)

        mail_entry = ttk.Entry(self.new_user)
        mail_entry.pack(pady=5, padx=10)

        username_label = ttk.Label(self.new_user, text="Enter your username:")
        username_label.pack(pady=10, padx=10)

        username_entry = ttk.Entry(self.new_user)
        username_entry.pack(pady=5, padx=10)

        password_label = ttk.Label(self.new_user, text="Enter your password:")
        password_label.pack(pady=10, padx=10)

        password_entry = ttk.Entry(self.new_user, show="*")
        password_entry.pack(pady=5, padx=10)

        self.new_user_text = ttk.Label(self.new_user, text="Add User")
        self.new_user_text.pack(pady=10, padx=10)

        self.new_user_button = ttk.Button(self.new_user, text="Add Account", command=lambda :self.check_and_send_new_user(username_entry.get(), password_entry.get(), mail_entry.get()))
        self.new_user_button.pack(pady=5, padx=10)

        self.new_user.grab_set()
        self.new_user.focus_set()
        self.new_user.wait_window()
    
    def check_and_send_new_user(self, username, password, mail):
        if mail.find("@") == -1:
            self.new_user_text.config(text="Please enter a valid mail.")
            return
        if not username or not password or not mail:
            self.new_user_text.config(text="Please fill all fields.")
            return
        
        self.client.sv_add_user(mail, password, username)
        if self.new_user:
            self.new_user.destroy()
        
            
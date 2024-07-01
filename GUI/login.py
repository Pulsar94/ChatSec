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
        self.username = ttk.Entry(self)
        self.username.pack(pady=5, padx=10)
        self.username.insert(0, "Username")
        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5, padx=10)
        self.password.insert(0, "Password")
        print("help1")
        self.login_button = ttk.Button(self, text="Login", command=self.login)
        print("help2")
        self.login_button.pack(pady=5, padx=10)
        print("help3")

    def login(self):
        self.controller.username = self.username.get()
        self.text= ttk.Label(self, text="Connexion en cours...")
        self.text.pack(pady=10, padx=10)
        print("help4")
        self.controller.show_frame("RoomPage")
        print("help5")
        self.controller.frames["RoomPage"].initialize_client()
        print("help6")
        sleep(0.3)
        self.controller.frames["RoomPage"].actualise()
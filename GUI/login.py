from tkinter import ttk

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
        login_button = ttk.Button(self, text="Login", command=self.login)
        login_button.pack(pady=5, padx=10)

    def login(self):
        self.controller.username = self.username.get()
        self.controller.show_frame("RoomPage")
        self.controller.frames["RoomPage"].initialize_client()
        self.controller.frames["RoomPage"].actualise()
import tkinter as tk
from tkinter import ttk

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Chat P2P")
        self.geometry("800x600")

        # Créer un conteneur
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (LoginPage, ChatPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # Mettre tous les cadres dans la même grille, l'un sur l'autre
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        '''Afficher un cadre pour le nom de page donné'''
        frame = self.frames[page_name]
        frame.tkraise()

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
        # Vous pouvez ajouter la logique de connexion ici
        self.controller.show_frame("ChatPage")

class ChatPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.chat_histories = {}

        self.create_widgets()

    def create_widgets(self):
        left_frame = ttk.Frame(self, width=200)
        left_frame.pack(side="left", fill="y")

        right_frame = ttk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True)

        user_list_label = ttk.Label(left_frame, text="Liste des utilisateurs")
        user_list_label.pack(pady=10, padx=10)

        self.user_list = tk.Listbox(left_frame)
        self.user_list.pack(fill="y", expand=True, pady=5, padx=10)
        self.user_list.bind("<<ListboxSelect>>", self.on_user_select)

        # Ajout des utilisateurs fictifs
        users = ["grp1", "grp2", "grp3"]
        for user in users:
            self.user_list.insert(tk.END, user)
            self.chat_histories[user] = []

        chat_label = ttk.Label(right_frame, text="Chat")
        chat_label.pack(pady=10, padx=10)

        self.chat_text = tk.Text(right_frame, state="disabled")
        self.chat_text.pack(fill="both", expand=True, pady=5, padx=10)

        self.message_entry = ttk.Entry(right_frame)
        self.message_entry.pack(fill="x", pady=5, padx=10)

        send_button = ttk.Button(right_frame, text="Envoyer", command=self.send_message)
        send_button.pack(pady=5, padx=10)

        self.current_user = None

    def on_user_select(self, event):
        selected_indices = self.user_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            self.current_user = self.user_list.get(selected_index)
            self.update_chat_history()

    def update_chat_history(self):
        self.chat_text.config(state="normal")
        self.chat_text.delete(1.0, tk.END)
        if self.current_user in self.chat_histories:
            for message in self.chat_histories[self.current_user]:
                self.chat_text.insert(tk.END, message + "\n")
        self.chat_text.config(state="disabled")

    def send_message(self):
        message = self.message_entry.get()
        if message and self.current_user:
            self.chat_histories[self.current_user].append("Vous: " + message)
            self.update_chat_history()
            self.message_entry.delete(0, tk.END)

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()

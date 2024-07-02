import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import base64

class ChatPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.chat_histories = self.controller.frames["RoomPage"].chat_histories
        self.client = controller.client
        self.create_widgets()

    def create_widgets(self):
        left_frame = ttk.Frame(self, width=200)
        left_frame.pack(side="left", fill="y")
        right_frame = ttk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True)
        user_list_label = ttk.Label(left_frame, text="Utilisateurs connectés")
        user_list_label.pack(pady=10, padx=10)
        self.user_list = tk.Listbox(left_frame)
        self.user_list.pack(fill="y", expand=True, pady=5, padx=10)
        chat_label = ttk.Label(right_frame, text="Chat")
        chat_label.pack(pady=10, padx=10)
        self.chat_text = tk.Text(right_frame, state="disabled")
        self.chat_text.pack(fill="both", expand=True, pady=5, padx=10)
        self.message_entry = ttk.Entry(right_frame)
        self.message_entry.bind("<Return>", self.clavier)
        self.message_entry.pack(fill="x", pady=5, padx=10)
        send_button = ttk.Button(right_frame, text="Envoyer", command=self.send_message)
        send_button.pack(pady=5, padx=10)
        send_file_button = ttk.Button(right_frame, text="Envoyer un fichier", command=self.select_and_send_file)
        send_file_button.pack(pady=5, padx=10)
        return_to_room = ttk.Button(right_frame, text="Retour aux salles", command=self.return_to_room)
        return_to_room.pack(pady=5, padx=10)

        self.current_room = None

    def update_users(self, users):
        if self.current_room:
            self.user_list.delete(0, tk.END)
            for user in users:
                self.user_list.insert(tk.END, user)

    def update_chat_history(self):
        if self.current_room in self.chat_histories:
            self.chat_text.config(state="normal")
            self.chat_text.delete(1.0, tk.END)
            for message in self.chat_histories[self.current_room]:
                self.chat_text.insert(tk.END, message + "\n")
            self.chat_text.config(state="disabled")

    def add_message(self, username, message):
        if self.current_room:
            self.chat_text.config(state="normal")
            self.chat_text.insert(tk.END, f"{username}: {message}\n")
            self.chat_text.config(state="disabled")

    def clavier(self, event):
        self.send_message()

    def send_message(self):
        message = self.message_entry.get()
        if message and self.current_room and self.client:
            username = self.controller.username
            self.client.rm_send_message(message, username)
            self.message_entry.delete(0, tk.END)

    def return_to_room(self):
        self.client.rm_disconnect()
        self.controller.show_frame("RoomPage")
        self.controller.frames["RoomPage"].request_rooms()

    def select_and_send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path and self.current_room and self.client:
            username = self.controller.username
            self.client.rm_send_file(file_path,self.current_room, username)
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
import socket
import shared.json_handler as jh
from client.client import Client
import base64

class ChatPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.chat_histories = self.controller.frames["RoomPage"].chat_histories
        self.client = None
        self.create_widgets()

    def create_widgets(self):
        left_frame = ttk.Frame(self, width=200)
        left_frame.pack(side="left", fill="y")
        right_frame = ttk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True)
        # user_list_label = ttk.Label(left_frame, text="Liste des rooms")
        # user_list_label.pack(pady=10, padx=10)
        # self.user_list = tk.Listbox(left_frame)
        # self.user_list.pack(fill="y", expand=True, pady=5, padx=10)
        # self.user_list.bind("<<ListboxSelect>>", self.on_room_select)
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

        self.current_room = None

    # def on_room_select(self, event):
    #     selected_indices = self.user_list.curselection()
    #     if selected_indices:
    #         selected_index = selected_indices[0]
    #         self.current_room = self.user_list.get(selected_index)
    #         self.update_chat_history()

    def update_chat_history(self):
        if self.current_room in self.chat_histories:
            self.chat_text.config(state="normal")
            self.chat_text.delete(1.0, tk.END)
            for message in self.chat_histories[self.current_room]:
                self.chat_text.insert(tk.END, message + "\n")
            self.chat_text.config(state="disabled")

    def clavier(self, event):
        self.send_message()

    def send_message(self):
        message = self.message_entry.get()
        if message and self.current_room and self.client:
            username = self.controller.username
            self.client.rm_send_message(jh.json_encode("room_message", {"username": username, "message": message}), self.current_room)
            self.message_entry.delete(0, tk.END)



    def select_and_send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path and self.current_room and self.client:
            username = self.controller.username
            self.client.rm_send_file(file_path,self.current_room, username)

    def initialize_client(self):
        self.client = Client()
        self.client.sv_connect(socket.gethostname(), 5000)
        threading.Thread(target=self.client.rm_listen).start()


class CountdownDialog(tk.Toplevel):
    def __init__(self, parent, file_name, username, timeout=30):
        super().__init__(parent)
        self.title("File Received")
        self.file_name = file_name
        self.timeout = timeout
        self.result = None
        
        self.label = ttk.Label(self, text=f"{username} wants to send you the file {file_name}. Do you want to accept?")
        self.label.pack(pady=10)

        self.countdown_label = ttk.Label(self, text=f"Time remaining: {self.timeout} seconds")
        self.countdown_label.pack(pady=10)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)
        
        self.accept_button = ttk.Button(self.button_frame, text="Accept", command=self.accept)
        self.accept_button.grid(row=0, column=0, padx=5)
        
        self.decline_button = ttk.Button(self.button_frame, text="Decline", command=self.decline)
        self.decline_button.grid(row=0, column=1, padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self.decline)  # Handle window close button
        
        self.start_countdown()

        # Center the dialog on the parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() // 2 - self.winfo_width() // 2
        y = parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f"+{x}+{y}")

    def start_countdown(self):
        if self.timeout > 0:
            self.timeout -= 1
            self.countdown_label.config(text=f"Time remaining: {self.timeout} seconds")
            self.after(1000, self.start_countdown)
        else:
            self.decline()

    def accept(self):
        self.result = True
        self.destroy()

    def decline(self):
        self.result = False
        self.destroy()

def on_file_received(parent, file_name, file_data):
    save_path = filedialog.asksaveasfilename(initialfile=file_name, title="Save File As")
    if save_path:
        with open(save_path, 'wb') as file:
            for seg in file_data:
                file.write(base64.b64decode(seg))
        print("File accepted and saved")
    else:
        print("File declined")
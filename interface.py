import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import base64
import os
import socket
import ssl
import json_handler as jh
from client_function import func
from certificate import get_or_generate_cert

CERT_FILE_SERVER = "key/server-cert.pem"
CERT_FILE_CLIENT = "key/client-cert.pem"
KEY_FILE_CLIENT = "key/client-key.pem"
CERT_EXPIRATION_DAYS = 1

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat P2P")
        self.geometry("800x600")
        self.username = None
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}
        for F in (LoginPage, ChatPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("LoginPage")

    def show_frame(self, page_name):
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
        self.controller.username = self.username.get()
        self.controller.show_frame("ChatPage")
        self.controller.frames["ChatPage"].initialize_client()

class ChatPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.chat_histories = {}
        self.client = None
        self.create_widgets()

    def create_widgets(self):
        left_frame = ttk.Frame(self, width=200)
        left_frame.pack(side="left", fill="y")
        right_frame = ttk.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True)
        user_list_label = ttk.Label(left_frame, text="Liste des rooms")
        user_list_label.pack(pady=10, padx=10)
        self.user_list = tk.Listbox(left_frame)
        self.user_list.pack(fill="y", expand=True, pady=5, padx=10)
        self.user_list.bind("<<ListboxSelect>>", self.on_room_select)
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

    def on_room_select(self, event):
        selected_indices = self.user_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            self.current_room = self.user_list.get(selected_index)
            self.update_chat_history()

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
        if message and self.current_room:
            username = self.controller.username
            self.client.send(jh.json_encode("room_message", {"room": self.current_room, "username": username, "message": message}))
            self.message_entry.delete(0, tk.END)

    def select_and_send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path and self.current_room:
            username = self.controller.username
            self.client.send_file(file_path, self.current_room, username)

    def initialize_client(self):
        self.client = Client(self)
        self.client.connect(socket.gethostname(), 5000)
        threading.Thread(target=self.client.listen).start()

class Client:
    def __init__(self, chat_page):
        self.chat_page = chat_page
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        cert_file, key_file = get_or_generate_cert(CERT_FILE_CLIENT, KEY_FILE_CLIENT, CERT_EXPIRATION_DAYS)
        self.context.load_verify_locations(CERT_FILE_SERVER)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.func = func()
        self.func.tag["room_message"] = self.room_message_received
        self.func.tag["room_file"] = self.room_file_received
        self.func.tag["room_file_seg"] = self.room_file_seg_received
        self.func.tag["room_file_seg_end"] = self.room_file_seg_end_received
        self.func.tag["file_accept_request"] = self.file_accept_request  # Nouvelle fonction
        self.files = {}

    def connect(self, host, port):
        self.ssl_clientsocket = self.context.wrap_socket(self.clientsocket, server_hostname=host)
        try:
            self.ssl_clientsocket.connect((host, port))
            print("Connected to server {} on port {}".format(host, port))
            self.chat_page.user_list.insert(tk.END, "room1")
            self.chat_page.chat_histories["room1"] = []
            self.send(jh.json_encode("create_room", {"name": "room1", "password": "1234"}))
        except Exception as e:
            print("Connection failed: ", e)

    def listen(self):
        while True:
            received = self.ssl_clientsocket.recv(1024).decode()
            if received:
                data = jh.json_decode(received)
                print("Server says: ", data)
                for tag, callback in self.func.tag.items():
                    if jh.compare_tag_from_socket(data, tag, callback, self.ssl_clientsocket):
                        print("Executed callback for tag", tag)
                        break

    def send(self, message):
        self.ssl_clientsocket.send(message.encode())

    def send_file(self, file_path, room, username):
        file_name = os.path.basename(file_path)
        self.ssl_clientsocket.send(jh.json_encode("room_file", {"room": room, "file_name": file_name, "username": username}).encode())
        with open(file_path, 'rb') as file:
            seg_count = 0
            seg = file.read(512)
            while seg:
                print("Sending file segment: ", seg_count)
                encoded_seg = base64.b64encode(seg).decode('utf-8')
                self.ssl_clientsocket.send(jh.json_encode("room_file_seg", {"room": room, "seg": seg_count, "file_name": file_name, "file": encoded_seg}).encode())
                seg = file.read(512)
                seg_count += 1
            print("Sending file segment: end")
            self.ssl_clientsocket.send(jh.json_encode("room_file_seg_end", {"room": room, "file_name": file_name}).encode())
    
    def room_message_received(self, data, socket):
        room = data["data"]["room"]
        username = data["data"]["username"]
        message = data["data"]["message"]
        full_message = f"{username}: {message}" 
        if room not in self.chat_page.chat_histories:
            self.chat_page.chat_histories[room] = []
        self.chat_page.chat_histories[room].append(full_message)
        if room == self.chat_page.current_room:
            self.chat_page.update_chat_history()

    def room_file_received(self, data, socket):
        file_name = data["data"]["file_name"]
        print(f"Initializing file reception for {file_name}")
        self.files[file_name] = []

    def room_file_seg_received(self, data, socket):
        file_name = data["data"]["file_name"]
        if file_name not in self.files:
            self.files[file_name] = []  # Initialize the file list if not already done
        self.files[file_name].append(data["data"]["file"])
        print(f"Received segment for {file_name}")

    def room_file_seg_end_received(self, data, socket):
        file_name = data["data"]["file_name"]
        file_data = self.files.get(file_name)

        if file_data is not None:
            # Appeler on_file_received dans le thread principal
            self.chat_page.controller.after(0, on_file_received, self.chat_page.controller, file_name, file_data)
            del self.files[file_name]
            print(f"File reception completed for {file_name}")
        else:
            print(f"Error: no data found for file {file_name}")

    def file_accept_request(self, data, socket):
        username = data["data"]["username"]
        file_name = data["data"]["file_name"]
        dialog = CountdownDialog(self.chat_page.controller, file_name, username)
        self.chat_page.controller.wait_window(dialog)
        if dialog.result:
            socket.send(jh.json_encode("file_accept_response", {"file_name": file_name, "accepted": True}).encode())
        else:
            socket.send(jh.json_encode("file_accept_response", {"file_name": file_name, "accepted": False}).encode())

    def __del__(self):
        self.clientsocket.close()

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

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()

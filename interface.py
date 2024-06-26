import time
import tkinter as tk
from tkinter import ttk
import threading as thread
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
        for F in (LoginPage, RoomPage, ChatPage):
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
        self.controller.show_frame("RoomPage")
        self.controller.frames["RoomPage"].initialize_client()
        self.controller.frames["RoomPage"].actualise()

class RoomPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.chat_histories = {}
        self.client = None
        self.room_list = None
        self.verif= True
        self.create_widgets()

    def create_widgets(self):
        label = ttk.Label(self, text="Liste des rooms")
        label.pack(pady=10, padx=10)
        self.room_list = tk.Listbox(self)
        self.room_list.pack(fill="both", expand=True, pady=5, padx=10)
        join_button = ttk.Button(self, text="Join", command=self.join_room)
        join_button.pack(pady=5, padx=10)
        create_button = ttk.Button(self, text="Create", command=self.createwindow)
        create_button.pack(pady=5, padx=10)
        actualise_button = ttk.Button(self, text=chr(0x21BB), command=self.actualise)
        actualise_button.pack(side="left",pady=5)


    def actualise(self):
        self.client.send(jh.json_encode("get_rooms", {}))
        time.sleep(0.01) # wait for the server to respond
        for r in (self.client.rooms):
            if r not in self.room_list.get(0, tk.END):
                self.room_list.insert(tk.END, r)


    def createwindow(self):
        self.popup = tk.Toplevel(self)
        self.popup.title("Create Room")
        self.popup.geometry("300x200")  # Width x Height

        label = ttk.Label(self.popup, text="Enter room name:")
        label.pack(pady=10, padx=10)
        

        self.room_name_entry = ttk.Entry(self.popup)
        self.room_name_entry.insert(0, "Room Name")
        self.room_name_entry.pack(pady=5, padx=10)

        label = ttk.Label(self.popup, text="Enter room password:")
        label.pack(pady=10, padx=10)

        self.room_password_entry = ttk.Entry(self.popup)
        self.room_password_entry.insert(0, "Password")
        self.room_password_entry.pack(pady=5, padx=10)
                                                                    #self.send(jh.json_encode("create_room", {"name": "room1", "password": "1234"}))
        create_room_button = ttk.Button(self.popup, text="Create Room", command=lambda :self.create_room(self.room_name_entry.get(),self.room_password_entry.get()))
        create_room_button.pack(pady=5, padx=10)

        # Optional: Focus on the popup and wait until it is closed
        self.popup.grab_set()
        self.popup.focus_set()
        self.popup.wait_window()

       
    def create_room(self,room_name,room_password):
        self.controller.frames["RoomPage"].client.send(jh.json_encode("create_room", {"name": room_name, "password": room_password}))
        self.controller.frames["RoomPage"].room_list.insert(tk.END, room_name)
        self.controller.frames["RoomPage"].chat_histories[room_name] = []
        self.popup.destroy()
                

    def initialize_client(self):
        self.client = Client(self)
        self.client.connect(socket.gethostname(), 5000)
        thread.Thread(target=self.client.listen).start()

    def join_room(self):
        selected_indices = self.room_list.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            self.selected_room = self.room_list.get(selected_index)
            self.room_verification(self.selected_room)


    def room_verification(self, room):
        self.room_verif = tk.Toplevel(self)
        self.room_verif.title("Create Room")
        self.room_verif.geometry("300x200")  # Width x Height

        label = ttk.Label(self.room_verif, text="Enter room password:")
        label.pack(pady=10, padx=10)

        self.room_password_entry = ttk.Entry(self.room_verif)
        self.room_password_entry.insert(0, "Password")
        self.room_password_entry.pack(pady=5, padx=10)

        self.room_verif_button = ttk.Button(self.room_verif, text="Join Room", command=lambda :self.room_verification_check(room,self.room_password_entry.get()))
        self.room_verif_button.pack(pady=5, padx=10)

        self.room_verif.grab_set()
        self.room_verif.focus_set()
        self.room_verif.wait_window()

    def room_verification_check(self,room,password):
        self.client.send(jh.json_encode("join_room", {"room": room})) # "password": password
        self.controller.show_frame("ChatPage")
        self.controller.frames["ChatPage"].current_room = self.selected_room
        self.controller.frames["ChatPage"].update_chat_history()
        self.controller.frames["ChatPage"].initialize_client()
        self.client.send(jh.json_encode("join_room", {"room": self.selected_room}))
        self.room_verif.destroy()

    def update_room_history(self):
        self.controller.frames["ChatPage"].update_chat_history()

class ChatPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.chat_histories = self.controller.frames["RoomPage"].chat_histories
        self.client = None
        self.create_widgets()

    def create_widgets(self):
        right_frame = ttk.Frame(self)
        right_frame.pack(fill="both", expand=True)
        chat_label = ttk.Label(right_frame, text="Chat")
        chat_label.pack(pady=10, padx=10)
        self.chat_text = tk.Text(right_frame, state="disabled")
        self.chat_text.see(tk.END)
        self.chat_text.pack(fill="both", expand=True, pady=5, padx=10)
        self.message_entry = ttk.Entry(right_frame)
        self.message_entry.bind("<Return>", self.clavier)
        self.message_entry.pack(fill="x", pady=5, padx=10)
        send_button = ttk.Button(right_frame, text="Envoyer", command=self.send_message)
        send_button.pack(pady=5, padx=10)
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

    def initialize_client(self):
        self.client = Client(self)
        self.client.connect(socket.gethostname(), 5000)
        thread.Thread(target=self.client.listen).start()

class Client:
    def __init__(self, chat_page):
        self.rooms = []
        self.chat_page = chat_page
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        cert_file, key_file = get_or_generate_cert(CERT_FILE_CLIENT, KEY_FILE_CLIENT, CERT_EXPIRATION_DAYS)
        self.context.load_verify_locations(CERT_FILE_SERVER)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.func = func()
        self.func.tag["room_message"] = self.room_message_received
        self.func.tag["list_rooms"] = self.list_rooms

    def connect(self, host, port):
        self.ssl_clientsocket = self.context.wrap_socket(self.clientsocket, server_hostname=host)
        try:
            self.ssl_clientsocket.connect((host, port))
            print("Connected to server {} on port {}".format(host, port))
            # self.chat_page.user_list.insert(tk.END, "room1")
            # self.chat_page.chat_histories["room1"] = []
            # self.send(jh.json_encode("create_room", {"name": "room1", "password": "1234"}))
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

    def room_message_received(self, data, socket):
        room = data["data"]["room"]
        username = data["data"]["username"]
        message = data["data"]["message"]
        full_message = f"{username}: {message}" 
        if room not in self.chat_page.chat_histories:
            self.chat_page.chat_histories[room] = []
        self.chat_page.chat_histories[room].append(full_message)
        if room == self.chat_page.selected_room:
            self.chat_page.update_room_history()

    def list_rooms(self, data, socket):
        self.rooms = jh.json_decode(data["data"])

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()


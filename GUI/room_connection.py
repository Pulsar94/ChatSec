from tkinter import ttk,messagebox
import tkinter as tk
import threading
import socket
from client.client import Client
import shared.json_handler as jh

class RoomPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.chat_histories = {}
        self.client = None
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
        if self.client:
            self.client.sv_send(jh.json_encode("get_rooms", {}))
            self.room_list.delete(0, tk.END)
            for r in self.client.room_list:
                self.room_list.insert(tk.END, r)

    def createwindow(self):
        self.popup = tk.Toplevel(self)
        self.popup.title("Create Room")
        self.popup.geometry("300x200")

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
        self.controller.frames["RoomPage"].client.sv_create_room(room_name, room_password)
        self.controller.frames["RoomPage"].room_list.insert(tk.END, room_name)
        self.controller.frames["RoomPage"].chat_histories[room_name] = []
        self.popup.destroy()
                

    def initialize_client(self):
        self.client = Client()
        self.client.sv_connect(socket.gethostname(), 5000)
        threading.Thread(target=self.client.sv_listen).start()

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
        if self.client :
            self.client.sv_connect_room(room, password) # "password": password
            self.controller.show_frame("ChatPage")
            self.controller.frames["ChatPage"].current_room = self.selected_room
            self.controller.frames["ChatPage"].update_chat_history()
            self.controller.frames["ChatPage"].initialize_client()
            self.room_verif.destroy()

    def update_room_history(self):
        self.controller.frames["ChatPage"].update_chat_history()

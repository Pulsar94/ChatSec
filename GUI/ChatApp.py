from GUI.LoginPage import LoginPage
from GUI.ChatPage import ChatPage
from GUI.RoomPage import RoomPage
import tkinter as tk
from tkinter import ttk
from os import path
from client.client import Client

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        icon_path = path.join(path.dirname(__file__), 'small_logo.png')  # Ensure this is the correct path
        self.icon_image = tk.PhotoImage(file=icon_path)
        self.iconphoto(False, self.icon_image)
        self.title("ChatRoom")
        self.geometry("800x600")
        self.username = None
        self.client = Client(self)
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}
        for F in (LoginPage, RoomPage, ChatPage):
            page_name = F.__name__
            self.frame = F(parent=container, controller=self)
            self.frames[page_name] = self.frame
            self.frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("LoginPage")
        
    def show_frame(self, page_name):
        self.frame = self.frames[page_name]
        self.frame.tkraise()

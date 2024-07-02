from GUI.login import LoginPage
from GUI.chat_room import ChatPage
from GUI.room_connection import RoomPage
from PIL import Image, ImageTk
import shared.json_handler as jh
from client.client import Client 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import base64
import os
import ssl


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(os.path.dirname(__file__), 'small_logo.png')  # Ensure this is the correct path
        self.icon_image = tk.PhotoImage(file=icon_path)
        self.iconphoto(False, self.icon_image)
        self.title("Chat P2P")
        self.geometry("800x600")
        self.username = None
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

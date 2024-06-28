from GUI.login import LoginPage
from GUI.chat_room import ChatPage
from GUI.room_connection import RoomPage
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
        self.show_frame("LoginPage")
        

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()

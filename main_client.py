from client.client import Client
from GUI.GUI import ChatApp
import threading as thread
import socket
import shared.json_handler as jh
import time

def main():
    print("---------------------------Starting client---------------------------")
    client = Client()
    app = ChatApp()
    app.mainloop()

main()
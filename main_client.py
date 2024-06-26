from client.client import Client
import threading as thread
import socket
import shared.json_handler as jh

def main():
    print("---------------------------Starting client---------------------------")
    client = Client()
    client.sv_connect(socket.gethostname(), 5000)
    thread.Thread(target=client.sv_listen).start()
    client.sv_create_room("room1", "123")
    #client.sv_connect_room("room1", "123")
    #client.rm_send_message("hello", "Tom")

main()
import socket
from shared.rsa_handler import RSAHandler as rsa
import server.rooms as rooms
import shared.json_handler as jh
import threading as thread
from server.server_function import func
from shared.certificate import get_or_generate_cert

CERT_FILE_SERVER = "key/server-cert.pem"
KEY_FILE_SERVER = "key/server-key.pem"

CERT_EXPIRATION_DAYS = 1

class Server:
    def __init__(self):
        self.rooms = rooms.Rooms()
        self.rsa = rsa(CERT_FILE_SERVER, KEY_FILE_SERVER, CERT_EXPIRATION_DAYS)
        
        self.func = func(self)
        
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((socket.gethostname(), 5000))
        self.serversocket.listen(5)
        print("Server is ready to receive a connection")

    def listen(self):
        while True:
            print("Waiting for connection")
            (clientsocket, address) = self.serversocket.accept()
            print("Connection from", address, ". Creating new thread")

            thread.Thread(target=self.handle_client, args=(clientsocket, address)).start()
    
    def handle_client(self, stream, address):
        while True:
            received = stream.recv(1024).decode()
            if received != "":
                data = jh.json_decode(received)
                print("Client says: ", data)

                for tag, callback in self.func.tag.items():
                    if jh.compare_tag_from_socket(data, tag, callback, stream):
                        print("Executed callback for tag", tag)
                        break

    def send(self, connstream, message):
        connstream.send(message.encode())

    def __del__(self):
        self.serversocket.close()

def main():
    print("---------------------------Starting server---------------------------")
    server = Server()
    server.listen()

main()

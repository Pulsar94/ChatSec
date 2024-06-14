import socket
import ssl
import rooms
import json_handler as jh
import threading as thread
from certificate import get_or_generate_cert

CERT_FILE_SERVER = "key/server-cert.pem"
KEY_FILE_SERVER = "key/server-key.pem"

CERT_EXPIRATION_DAYS = 1

class Server:
    def __init__(self):
        self.rooms = rooms.Rooms()
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        cert, key = get_or_generate_cert(CERT_FILE_SERVER, KEY_FILE_SERVER, CERT_EXPIRATION_DAYS)
        self.context.load_cert_chain(certfile=cert, keyfile=key)
        
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((socket.gethostname(), 5000))
        self.serversocket.listen(5)
        print("Server is ready to receive a connection")

    def listen(self):
        while True:
            (clientsocket, address) = self.serversocket.accept()
            print("Connection from", address, ". Creating new thread")
            thread.Thread(target=self.handle_client, args=(clientsocket, address)).start()
    
    def handle_client(self, socket, address):
        stream = self.context.wrap_socket(socket, server_side=True)
        data = jh.json_decode(stream.recv(1024).decode())
        print("Client says: ", data)

        for k, v in self.tag.items():
            if jh.compare_tag_from_socket(data, k, v, stream):
                print("Executed callback for tag", k)
                break

    def send(self, connstream, message):
        connstream.send(message.encode())
        connstream.close()

    def __del__(self):
        self.serversocket.close()

def main():
    server = Server()
    server.listen()

main()

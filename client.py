import socket
import ssl
import threading as thread
import json_handler as jh
from certificate import get_or_generate_cert

CERT_FILE_SERVER = "key/server-cert.pem"

CERT_FILE_CLIENT = "key/client-cert.pem"
KEY_FILE_CLIENT = "key/client-key.pem"

CERT_EXPIRATION_DAYS = 1

class Client:
    def __init__(self):
        
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.cert_file, self.key_file = get_or_generate_cert(CERT_FILE_CLIENT, KEY_FILE_CLIENT, CERT_EXPIRATION_DAYS)
        self.context.load_verify_locations(self.cert_file)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.ssl_clientsocket = self.context.wrap_socket(self.clientsocket, server_hostname=host)
        try:
            self.ssl_clientsocket.connect((host, port))
            print("Connected to server {} on port {}".format(host, port))
        except:
            print("Connection failed")
    
    def listen(self):
        while True:
            data = self.ssl_clientsocket.recv(1024).decode()
            print("Server says: ", data)
        
    def send(self, message):
        self.ssl_clientsocket.send(message.encode())
        
    def receive(self):
        return self.ssl_clientsocket.recv(1024).decode()
    
    def __del__(self):
        self.clientsocket.close()

def main():
    client = Client()
    client.connect(socket.gethostname(), 5000)
    thread.Thread(target=client.listen).start()
    data = jh.json_encode("create_room", {"name": "room1", "password": "1234"})
    client.send(data)
    data = jh.json_encode("room_message", {"room": "room1", "message": "Hello, world!"})
    
    
main()

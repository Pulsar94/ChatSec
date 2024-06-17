import socket
import ssl
import threading as thread
import json_handler as jh
from client_function import func
from certificate import get_or_generate_cert

CERT_FILE_SERVER = "key/server-cert.pem"

CERT_FILE_CLIENT = "key/client-cert.pem"
KEY_FILE_CLIENT = "key/client-key.pem"

CERT_EXPIRATION_DAYS = 1

class Client:
    def __init__(self):
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.cert_file, self.key_file = get_or_generate_cert(CERT_FILE_CLIENT, KEY_FILE_CLIENT, CERT_EXPIRATION_DAYS)
        self.context.load_verify_locations(CERT_FILE_SERVER)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.func = func()

    def connect(self, host, port):
        self.ssl_clientsocket = self.context.wrap_socket(self.clientsocket, server_hostname=host)
        try:
            self.ssl_clientsocket.connect((host, port))
            print("Connected to server {} on port {}".format(host, port))
        except:
            print("Connection failed")
    
    def listen(self):
        while True:
            received = self.ssl_clientsocket.recv(1024).decode()
            if received != "":
                data = jh.json_decode(received)
                print("Server says: ", data)

                for tag, callback in self.func.tag.items():
                    if jh.compare_tag_from_socket(data, tag, callback, self.ssl_clientsocket):
                        print("Executed callback for tag", tag)
                        break
        
    def send(self, message):
        self.ssl_clientsocket.send(message.encode())
    
    def __del__(self):
        self.clientsocket.close()

def main():
    client = Client()
    client.connect(socket.gethostname(), 5000)
    #thread.Thread(target=client.listen).start()
    
    print("Client is ready to send to server")

    client.send(jh.json_encode("create_room", {"name": "room1", "password": "1234"}))
    print(client.ssl_clientsocket.recv(1024).decode())
    
    client.send(jh.json_encode("connect_room", {"name": "room1"}))

    client.send(jh.json_encode("room_message", {"room": "room1", "message": "Hello, world!"}))
    print(client.ssl_clientsocket.recv(1024).decode())
    print(client.ssl_clientsocket.recv(1024).decode())
    
    client.send(jh.json_encode("room_disconnect", {"room": "room1"}))
    print(client.ssl_clientsocket.recv(1024).decode())
    
main()

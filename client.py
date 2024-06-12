import socket
import ssl
import os
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

CERT_FILE = "key/server-cert.pem"
KEY_FILE = "key/client.pem"
CERT_EXPIRATION_DAYS = 1
SERVER_IP = '10.10.0.3'

class Client:
    def __init__(self):
        
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        #cert_file, key_file = self.get_or_generate_cert()
        self.context.load_verify_locations(CERT_FILE)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        self.ssl_clientsocket = self.context.wrap_socket(self.clientsocket, server_hostname=host)
        self.ssl_clientsocket.connect((host, port))
        print("Connected to server")
        
    def send(self, message):
        self.ssl_clientsocket.send(message.encode())
        
    def receive(self):
        return self.ssl_clientsocket.recv(1024).decode()
    
    def __del__(self):
        self.clientsocket.close()

def main():
    client = Client()
    client.connect(socket.gethostname(), 5000)
    client.send("Hello, server!")
    print(client.receive())
    
main()

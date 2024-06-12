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

CERT_FILE_SERVER = "key/server-cert.pem"
KEY_FILE_SERVER = "key/server-key.pem"
CERT_EXPIRATION_DAYS = 1

class Client_data:
    def __init__(self):
        self.client = {}

    def add_client(self, socket, name):
        self.client[name] = {socket}

    def get_client(self, name):
        return self.client[name]

    def remove_client(self, name):
        del self.client[name]

class Server:
    def __init__(self, data=Client_data()):
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        CERT_FILE_SERVER, KEY_FILE_SERVER = self.get_or_generate_cert()
        self.context.load_cert_chain(certfile=CERT_FILE_SERVER, keyfile=KEY_FILE_SERVER)
        
        self.data = data
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((socket.gethostname(), 5000))
        self.serversocket.listen(5)
        print("Server is ready to receive a connection")

    def get_or_generate_cert(self):
        if os.path.exists(CERT_FILE_SERVER) and os.path.exists(KEY_FILE_SERVER):
            cert = x509.load_pem_x509_certificate(open(CERT_FILE_SERVER, 'rb').read(), default_backend())
            if cert.not_valid_after_utc > datetime.datetime.now(datetime.UTC):
                return CERT_FILE_SERVER, KEY_FILE_SERVER
        
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        cert = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.UTC))
            .not_valid_after(datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=CERT_EXPIRATION_DAYS))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost")]), critical=False)
            .sign(key, hashes.SHA256(), default_backend())
        )
        
        with open(CERT_FILE_SERVER, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(KEY_FILE_SERVER, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return CERT_FILE_SERVER, KEY_FILE_SERVER

    def receive(self):
        (clientsocket, address) = self.serversocket.accept()
        print("Connection from", address)
        connstream = self.context.wrap_socket(clientsocket, server_side=True)
        print("Client says: ", connstream.recv(1024).decode())
        return connstream, address

    def send(self, connstream, message):
        connstream.send(message.encode())

    def __del__(self):
        self.serversocket.close()

def main():
    server = Server()
    (connstream, address) = server.receive()
    server.send(connstream, "Hello, client!")

main()

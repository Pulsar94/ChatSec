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

CERT_FILE = "server.crt"
KEY_FILE = "server.key"
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
        self.data = data
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((socket.gethostname(), 5000))
        self.serversocket.listen(5)
        print("Server is ready to receive a connection")

        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        cert_file, key_file = self.get_or_generate_cert()
        self.context.load_verify_locations("ca_cert.pem")
        self.context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    def get_or_generate_cert(self):
        if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
            return self.generate_self_signed_cert()

        cert_valid = False
        try:
            with open(CERT_FILE, "rb") as cert_file:
                cert_data = cert_file.read()
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
                if cert.not_valid_after_utc > datetime.datetime.now(datetime.timezone.utc):
                    cert_valid = True
        except Exception as e:
            print(f"Error checking certificate validity: {e}")

        if not cert_valid:
            return self.generate_self_signed_cert()
        
        return CERT_FILE, KEY_FILE

    def generate_self_signed_cert(self):
        with open("ca_key.pem", "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
        with open("ca_cert.pem", "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open(KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Ile-de-France"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Villejuif"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Efrei Paris"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.now(datetime.timezone.utc)
        ).not_valid_after(
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=CERT_EXPIRATION_DAYS)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        ).sign(ca_key, hashes.SHA256())

        with open(CERT_FILE, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        return CERT_FILE, KEY_FILE

    def receive(self):
        (clientsocket, address) = self.serversocket.accept()
        connstream = self.context.wrap_socket(clientsocket, server_side=True)
        print("Connection from", address)
        print("Client says: ", connstream.recv(1024).decode())
        return connstream, address

    def send(self, connstream, message):
        connstream.send(message.encode())

    def __del__(self):
        self.serversocket.close()

    def process_PK_request(self, connstream, address):
        print("Processing PK request")
        connstream.send("PK".encode())

    def process_PK_response(self, connstream, address):
        print("Processing PK authentication")
        name = connstream.recv(1024).decode()
        self.data.add_client(connstream, name)
        self.send(connstream, "PK received")

    def process_PK_request_data(self, connstream, address):
        print("Processing PK request from data")
        name = connstream.recv(1024).decode()
        data_requested = self.data.get_client(name)
        if data_requested:
            self.send(connstream, data_requested)

def main():
    server = Server()
    (connstream, address) = server.receive()
    server.send(connstream, "Hello, client!")

main()

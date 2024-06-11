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

CERT_FILE = "client.crt"
KEY_FILE = "client.key"
CERT_EXPIRATION_DAYS = 1

class Client:
    def __init__(self):
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        cert_file, key_file = self.get_or_generate_cert()
        self.context.load_verify_locations("ca_cert.pem")
        self.context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED

    def get_or_generate_cert(self):
        if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
            return self.generate_self_signed_cert()

        cert_valid = False
        try:
            with open(CERT_FILE, "rb") as cert_file:
                cert_data = cert_file.read()
                cert = x509.load_pem_x509_certificate(cert_data, default_backend())
                if cert.not_valid_after > datetime.datetime.now(datetime.timezone.utc):
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

    def connect(self, host, port):
        self.clientsocket = self.context.wrap_socket(self.clientsocket, server_hostname=host)
        self.clientsocket.connect((host, port))
        print("Connected to server")
        
    def send(self, message):
        self.clientsocket.send(message.encode())
        
    def receive(self):
        return self.clientsocket.recv(1024).decode()

    def listen(self, time):
        server_response = ""
        while time > 0:
            server_response = self.receive()
            if server_response:
                print(server_response)
                break
            time -= 1
        return server_response
    
    def __del__(self):
        self.clientsocket.close()

def main():
    client = Client()
    client.connect(socket.gethostname(), 5000)
    client.send("Hello, server!")
    print(client.listen(500))
    
main()

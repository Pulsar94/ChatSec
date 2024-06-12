import socket
import ssl
import os
import datetime

CERT_FILE_SERVER = "key/server-cert.pem"
CERT_EXPIRATION_DAYS = 1

class Client:
    def __init__(self):
        
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        #cert_file, key_file = self.get_or_generate_cert()
        self.context.load_verify_locations(CERT_FILE_SERVER)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.path.exists(CERT_FILE_CLIENT) and os.path.exists(CERT_FILE_CLIENT):
            cert = x509.load_pem_x509_certificate(open(CERT_FILE_CLIENT, 'rb').read(), default_backend())
            if cert.not_valid_after_utc > datetime.datetime.now(datetime.UTC):
                return CERT_FILE_CLIENT, KEY_FILE_CLIENT
        
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
        
        with open(KEY_FILE_CLIENT, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return CERT_FILE_CLIENT, KEY_FILE_CLIENT

    def connect(self, host, port):
        self.ssl_clientsocket = self.context.wrap_socket(self.clientsocket, server_hostname=host)
        try:
            self.ssl_clientsocket.connect((host, port))
            print("Connected to server {} on port {}".format(host, port))
        except:
            print("Connection failed")
        
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

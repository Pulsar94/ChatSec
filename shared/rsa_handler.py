import rsa
from shared.certificate import get_or_generate_cert

class RSAHandler:
    def __init__(self, cert_file, key_file, cert_expiration_days):
        self.cert_file, self.key_file = get_or_generate_cert(cert_file, key_file, cert_expiration_days)
        self.private_key = self.get_private_key(self.key_file)
        self.public_key = self.get_public_key(self.cert_file)
    
    def get_private_key(self, key_type):
        with open(key_type, mode='rb') as file:
            key_data = file.read()
            return rsa.PrivateKey.load_pkcs1(key_data)

    def get_public_key(self, key_type):
        with open(key_type, mode='rb') as file:
            key_data = file.read()
            return rsa.PublicKey.load_pkcs1(key_data)

    def encrypt(self, data, pkey):
        return rsa.encrypt(data, pkey)

    def decrypt(self, data):
        return rsa.decrypt(data, self.private_key)



import rsa
from json import JSONDecodeError, loads
from re import findall
from shared.certificate import get_or_generate_cert

class RSAHandler:
    def __init__(self, cert_file, key_file, cert_expiration_days, pub_key_file):
        get_or_generate_cert(cert_file, key_file, cert_expiration_days, pub_key_file)
        self.private_key = self.get_private_key(key_file)
        self.public_key = self.get_public_key(pub_key_file)
    
    def get_private_key(self, key_type):
        with open(key_type, mode='rb') as file:
            key_data = file.read()
            return rsa.PrivateKey.load_pkcs1(key_data)

    def get_public_key(self, key_type):
        with open(key_type, mode='rb') as file:
            key_data = file.read()
            return rsa.PublicKey.load_pkcs1(key_data)
    
    def is_encrypted(self, data):
        try:
            loads(data.decode())
            return False
        except:
            return True

    def encrypt(self, data, pkey):
        return rsa.encrypt(data, pkey)

    def decrypt(self, data):
        return rsa.decrypt(data, self.private_key)



import rsa
from certificate import get_or_generate_cert

class RSAHandler:
    def __init__(self, cert_file, key_file, cert_expiration_days):
        self.cert_file, self.key_file = get_or_generate_cert(cert_file, key_file, cert_expiration_days)
        self.private_key = self.get_key(self.key_file, True)
        self.public_key = self.get_key(self.cert_file)
    
    def get_key(self, key_type , private=False):
        key = None
        with open(key_type, mode='rb') as file:
            key_data = file.read()
            if private:
                key = rsa.PrivateKey.load_pkcs1(key_data)
            else:
                key = rsa.PublicKey.load_pkcs1(key_data)
        return key

    def encrypt(self, data, pkey):
        return rsa.encrypt(data, pkey)

    def decrypt(self, data):
        return rsa.decrypt(data, self.private_key)



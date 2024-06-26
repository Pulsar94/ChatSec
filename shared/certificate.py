import os
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def get_or_generate_cert(cert_file, key_file, cert_expiration_days, pub_key_file=None):
        if os.path.exists(cert_file) and os.path.exists(key_file):
            cert = x509.load_pem_x509_certificate(open(cert_file, 'rb').read(), default_backend())
            if cert.not_valid_after_utc > datetime.datetime.now(datetime.UTC):
                return cert_file, key_file
        
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
            .not_valid_after(datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=cert_expiration_days))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost")]), critical=False)
            .sign(key, hashes.SHA256(), default_backend())
        )

        os.makedirs(os.path.dirname(cert_file), exist_ok=True)
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_file, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        if pub_key_file is not None:
            public_key = key.public_key()
            with open(pub_key_file, "wb") as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.PKCS1
                ))
        
        return cert_file, key_file, pub_key_file
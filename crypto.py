from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet
import os

class CryptoProvider:
    def __init__(self):
        # Generate a new RSA key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Extract the public key
        self.public_key = self.private_key.public_key()

    def get_public_key(self):
        # Return the public key in a format that can be sent over the network
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem

    def get_private_key(self):
        # Return the private key in a format that can be saved/loaded from disk
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem

    def generate_seed(self):
        # Generate a random seed
        return os.urandom(16)

    def generate_symmetric_key(self, seed):
        # Generate a symmetric key from the seed
        return Fernet.generate_key()

    def encrypt_with_public_key(self, message, public_key):
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def decrypt_with_private_key(self, ciphertext):
        plaintext = self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    def encrypt_with_symmetric_key(self, message, symmetric_key):
        cipher_suite = Fernet(symmetric_key)
        cipher_text = cipher_suite.encrypt(message)
        return cipher_text

    def decrypt_with_symmetric_key(self, cipher_text, symmetric_key):
        cipher_suite = Fernet(symmetric_key)
        plain_text = cipher_suite.decrypt(cipher_text)
        return plain_text

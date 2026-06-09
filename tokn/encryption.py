import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


def gen_password_key(password: bytes, salt: bytes) -> bytes:
    kdf = Argon2id(
        salt=salt, length=32, iterations=1, lanes=4, memory_cost=2**21  # 2.09 gb
    )

    key = kdf.derive(password)
    return base64.urlsafe_b64encode(key)


def encrypt_to_file(filename: str, text: str, salt: bytes, key: bytes) -> None:
    fernet = Fernet(key)
    token = fernet.encrypt(text.encode())

    with open(filename, "wb") as f:
        f.write(base64.b64encode(salt))
        f.write(b"\n")
        f.write(token)


def get_file_info(filename: str):
    with open(filename, "r") as f:
        salt, encrypted = f.read().splitlines()
    
    salt = base64.b64decode(salt) 

    return salt, encrypted

def decrypt(encrypted: bytes, key: bytes):
    fernet = Fernet(key)
    
    decrypted = fernet.decrypt(encrypted)
    
    return decrypted.decode()
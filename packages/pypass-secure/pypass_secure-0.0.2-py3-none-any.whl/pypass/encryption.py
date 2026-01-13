import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(
        kdf.derive(password.encode())
    )

def encrypt(text: str, key: bytes) -> bytes:
    return Fernet(key).encrypt(text.encode())

def decrypt(token: bytes, key: bytes) -> str:
    return Fernet(key).decrypt(token).decode()


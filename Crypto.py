# Crypto.py
import os
from cryptography.fernet import Fernet

KEY_FILE = os.path.expanduser("~/.qsologbook.key")

def _load_or_create_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        os.chmod(KEY_FILE, 0o600)  # owner-only
    with open(KEY_FILE, "rb") as f:
        return f.read()

FERNET = Fernet(_load_or_create_key())

def encrypt_text(plain: str) -> str:
    token = FERNET.encrypt(plain.encode("utf-8"))
    return "enc:" + token.decode("utf-8")

def decrypt_text(value: str) -> str:
    if value.startswith("enc:"):
        token = value[4:].encode("utf-8")
        return FERNET.decrypt(token).decode("utf-8")
    return value  # not encrypted

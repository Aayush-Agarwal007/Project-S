from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # For dev only: you may auto-generate a key on first run.
    # In production, **always** set via env and protect it.
    ENCRYPTION_KEY = Fernet.generate_key().decode()

fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def encrypt_value(plaintext: str) -> str:
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_value(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
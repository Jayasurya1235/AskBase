from cryptography.fernet import Fernet

from app.core.config import settings

_fernet = Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_text(plain_text: str) -> str:
    """Turns readable text into an encrypted string safe to store."""
    return _fernet.encrypt(plain_text.encode()).decode()


def decrypt_text(encrypted_text: str) -> str:
    """Reverses encrypt_text — turns stored ciphertext back into readable text."""
    return _fernet.decrypt(encrypted_text.encode()).decode()
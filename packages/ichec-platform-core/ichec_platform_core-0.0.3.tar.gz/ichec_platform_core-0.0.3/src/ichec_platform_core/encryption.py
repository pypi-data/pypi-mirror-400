import os
from cryptography.fernet import Fernet

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    """
    Get or create Fernet instance with lazy initialization
    """

    global _fernet
    if _fernet is None:
        key_str = os.environ.get("FERNET_KEY")
        if not key_str:
            raise RuntimeError("FERNET_KEY not set in configuration.")
        _fernet = Fernet(key_str.encode())
    return _fernet


def reset_fernet():
    """
    Reset Fernet instance (useful for testing)
    """

    global _fernet
    _fernet = None


def encrypt(payload: str) -> str:
    """
    Encrypt text using Fernet
    """

    return _get_fernet().encrypt(payload.encode()).decode()


def decrypt(payload: str) -> str:
    """
    Decrypt token using Fernet
    """

    return _get_fernet().decrypt(payload.encode()).decode()

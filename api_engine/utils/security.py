"""
Security utilities for the API Engine.
"""
import os
import hashlib
import secrets
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64


def generate_api_key(length: int = 32) -> str:
    """Generate a secure random API key."""
    return secrets.token_urlsafe(length)


def hash_password(password: str, salt: Optional[bytes] = None) -> tuple:
    """
    Hash a password using PBKDF2.
    
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def verify_password(password: str, hashed: bytes, salt: bytes) -> bool:
    """Verify a password against a hash."""
    try:
        new_hash, _ = hash_password(password, salt)
        return new_hash == hashed
    except Exception:
        return False


def encrypt_data(data: str, key: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """
    Encrypt data using Fernet symmetric encryption.
    
    Returns:
        Tuple of (encrypted_data, encryption_key)
    """
    if key is None:
        key = Fernet.generate_key()
    
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return encrypted, key


def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    """Decrypt data using Fernet."""
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data, showing only last few characters."""
    if len(data) <= visible_chars:
        return "*" * len(data)
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


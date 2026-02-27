# -*- encoding: utf-8 -*-

import logging
from cryptography.fernet import Fernet
from flask import current_app

logger = logging.getLogger(__name__)


def get_fernet():
    """Get Fernet instance using the app's FERNET_KEY."""
    key = current_app.config['FERNET_KEY']
    if not key:
        raise ValueError("FERNET_KEY is not configured. Generate one with: "
                         "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_token(plaintext):
    """Encrypt a token string. Returns base64-encoded ciphertext string."""
    return get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext):
    """Decrypt a token string. Returns plaintext string."""
    return get_fernet().decrypt(ciphertext.encode()).decode()

"""
Encryption utilities using Fernet symmetric encryption.

This module provides functions for encrypting and decrypting sensitive values
such as API keys and tokens stored in the database.
"""

import base64
import hashlib
from typing import Optional

import structlog
from cryptography.fernet import Fernet, InvalidToken

logger = structlog.get_logger()


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.

    Returns:
        str: A URL-safe base64-encoded 32-byte key.
    """
    return Fernet.generate_key().decode("utf-8")


def derive_key_from_password(password: str, salt: Optional[str] = None) -> bytes:
    """
    Derive a 32-byte encryption key from a password using PBKDF2.

    Args:
        password: The password to derive the key from.
        salt: Optional salt for key derivation. If None, uses a default salt.

    Returns:
        bytes: A 32-byte key suitable for Fernet encryption.
    """
    if salt is None:
        salt = "default-encryption-salt"

    # Use PBKDF2 to derive a secure key
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100000,
        dklen=32,
    )
    # Fernet requires URL-safe base64 encoding
    return base64.urlsafe_b64encode(derived)


def encrypt_value(value: str, key: bytes) -> str:
    """
    Encrypt a string value using Fernet symmetric encryption.

    Args:
        value: The plaintext value to encrypt.
        key: The encryption key as bytes.

    Returns:
        str: The encrypted value as a string.

    Raises:
        ValueError: If the value is empty or key is invalid.
    """
    if not value:
        logger.warning("Attempted to encrypt empty value")
        raise ValueError("Cannot encrypt empty value")

    try:
        fernet = Fernet(key)
        encrypted_bytes = fernet.encrypt(value.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error("Encryption failed", error=str(e))
        raise ValueError(f"Encryption failed: {e}") from e


def decrypt_value(token: str, key: bytes) -> str:
    """
    Decrypt a Fernet-encrypted value.

    Args:
        token: The encrypted value as a string.
        key: The encryption key as bytes.

    Returns:
        str: The decrypted plaintext value.

    Raises:
        InvalidToken: If the token is invalid or corrupted.
        ValueError: If decryption fails.
    """
    if not token:
        logger.warning("Attempted to decrypt empty token")
        raise ValueError("Cannot decrypt empty token")

    try:
        fernet = Fernet(key)
        decrypted_bytes = fernet.decrypt(token.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except InvalidToken as e:
        logger.warning("Invalid decryption token provided")
        raise InvalidToken("Invalid or corrupted encryption token") from e
    except Exception as e:
        logger.error("Decryption failed", error=str(e))
        raise ValueError(f"Decryption failed: {e}") from e

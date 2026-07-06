"""
Unit tests for encryption utilities.
"""

import pytest
from cryptography.fernet import Fernet, InvalidToken

from app.utils.crypto import (
    derive_key_from_password,
    decrypt_value,
    encrypt_value,
    generate_encryption_key,
)


class TestGenerateEncryptionKey:
    """Tests for the generate_encryption_key function."""

    def test_generates_valid_fernet_key(self) -> None:
        """Test that generated key is valid for Fernet."""
        key = generate_encryption_key()
        # Should not raise an exception
        Fernet(key.encode("utf-8"))

    def test_generates_unique_keys(self) -> None:
        """Test that each call generates a unique key."""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()
        assert key1 != key2

    def test_key_is_string(self) -> None:
        """Test that the returned key is a string."""
        key = generate_encryption_key()
        assert isinstance(key, str)


class TestDeriveKeyFromPassword:
    """Tests for the derive_key_from_password function."""

    def test_derives_consistent_key_same_password(self) -> None:
        """Test that same password produces same key."""
        password = "test-password"
        key1 = derive_key_from_password(password)
        key2 = derive_key_from_password(password)
        assert key1 == key2

    def test_derives_different_key_different_password(self) -> None:
        """Test that different passwords produce different keys."""
        key1 = derive_key_from_password("password1")
        key2 = derive_key_from_password("password2")
        assert key1 != key2

    def test_derives_different_key_different_salt(self) -> None:
        """Test that different salts produce different keys."""
        password = "test-password"
        key1 = derive_key_from_password(password, salt="salt1")
        key2 = derive_key_from_password(password, salt="salt2")
        assert key1 != key2

    def test_returns_bytes(self) -> None:
        """Test that the derived key is bytes."""
        key = derive_key_from_password("test")
        assert isinstance(key, bytes)

    def test_key_is_valid_for_fernet(self) -> None:
        """Test that derived key works with Fernet."""
        key = derive_key_from_password("test-password")
        # Should not raise an exception
        Fernet(key)


class TestEncryptValue:
    """Tests for the encrypt_value function."""

    def test_encrypt_and_decrypt_roundtrip(self) -> None:
        """Test that encrypted value can be decrypted."""
        key = generate_encryption_key().encode("utf-8")
        plaintext = "secret-api-key-12345"
        encrypted = encrypt_value(plaintext, key)
        decrypted = decrypt_value(encrypted, key)
        assert decrypted == plaintext

    def test_encrypt_produces_different_output_each_time(self) -> None:
        """Test that encryption includes timestamp/nonce."""
        key = generate_encryption_key().encode("utf-8")
        plaintext = "same-text"
        encrypted1 = encrypt_value(plaintext, key)
        encrypted2 = encrypt_value(plaintext, key)
        # Fernet includes timestamp, so outputs should differ
        assert encrypted1 != encrypted2

    def test_encrypt_empty_value_raises_error(self) -> None:
        """Test that encrypting empty value raises ValueError."""
        key = generate_encryption_key().encode("utf-8")
        with pytest.raises(ValueError):
            encrypt_value("", key)

    def test_encrypt_unicode_characters(self) -> None:
        """Test that unicode characters are handled correctly."""
        key = generate_encryption_key().encode("utf-8")
        plaintext = "secret-🔑-key-日本語"
        encrypted = encrypt_value(plaintext, key)
        decrypted = decrypt_value(encrypted, key)
        assert decrypted == plaintext


class TestDecryptValue:
    """Tests for the decrypt_value function."""

    def test_decrypt_with_wrong_key_raises_invalid_token(self) -> None:
        """Test that decrypting with wrong key raises InvalidToken."""
        key1 = generate_encryption_key().encode("utf-8")
        key2 = generate_encryption_key().encode("utf-8")
        plaintext = "secret-value"
        encrypted = encrypt_value(plaintext, key1)
        with pytest.raises(InvalidToken):
            decrypt_value(encrypted, key2)

    def test_decrypt_corrupted_token_raises_error(self) -> None:
        """Test that decrypting corrupted token raises error."""
        key = generate_encryption_key().encode("utf-8")
        with pytest.raises((InvalidToken, ValueError)):
            decrypt_value("corrupted-token-not-valid", key)

    def test_decrypt_empty_token_raises_error(self) -> None:
        """Test that decrypting empty token raises ValueError."""
        key = generate_encryption_key().encode("utf-8")
        with pytest.raises(ValueError):
            decrypt_value("", key)

    def test_decrypt_preserves_original_value(self) -> None:
        """Test that decryption returns exact original value."""
        key = generate_encryption_key().encode("utf-8")
        test_values = [
            "simple-text",
            "text-with-numbers-12345",
            "special-chars-!@#$%",
            "unicode-🎉-emoji",
        ]
        for original in test_values:
            encrypted = encrypt_value(original, key)
            decrypted = decrypt_value(encrypted, key)
            assert decrypted == original

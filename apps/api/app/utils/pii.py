"""
PII (Personally Identifiable Information) redaction utilities.

This module provides functions for hashing emails, masking phone numbers,
and recursively redacting PII from data structures.
"""

import hashlib
from typing import Any

import structlog

logger = structlog.get_logger()


def hash_email(email: str, salt: str) -> str:
    """
    Hash an email address using SHA-256 with a salt.

    Args:
        email: The email address to hash.
        salt: The salt to use for hashing.

    Returns:
        str: The hexadecimal hash digest.
    """
    normalized_email = email.lower().strip()
    salted_value = f"{salt}{normalized_email}{salt}"
    return hashlib.sha256(salted_value.encode("utf-8")).hexdigest()


def mask_phone(phone: str) -> str:
    """
    Mask a phone number while preserving its original formatting.

    Keeps the last 4 digits and all leading digits visible, and masks the up-to
    3 digits immediately before the last 4 (the local exchange). Separators and
    a leading ``+`` are preserved. Numbers with fewer than 4 digits are fully
    masked.

    Examples:
        +1-555-123-4567  -> +1-555-XXX-4567
        5551234567       -> 555XXX4567
        +44 20 7946 0958 -> +44 20 7XXX 0958
        123              -> XXX

    Args:
        phone: The phone number to mask.

    Returns:
        str: The masked phone number with original formatting preserved.
    """
    digit_positions = [i for i, ch in enumerate(phone) if ch.isdigit()]
    n = len(digit_positions)

    if n < 4:
        # Too short to partially mask meaningfully - mask everything.
        if n == 0:
            return phone
        logger.warning("Phone number too short to mask partially", phone_length=n)
        return "X" * n

    # Mask up to 3 digits immediately before the final 4 (keep last 4 visible).
    mask_count = min(3, n - 4)
    mask_digit_indices = set(range(n - 4 - mask_count, n - 4))

    chars = list(phone)
    for digit_index, position in enumerate(digit_positions):
        if digit_index in mask_digit_indices:
            chars[position] = "X"
    return "".join(chars)


def redact_pii(data: dict[str, Any], salt: str = "default-salt") -> dict[str, Any]:
    """
    Recursively walk a dictionary and redact PII fields.

    Applies hashing to 'email' fields and masking to 'phone' fields.

    Args:
        data: The dictionary to redact.
        salt: The salt to use for email hashing.

    Returns:
        dict: A new dictionary with PII fields redacted.
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if key.lower() == "email" and isinstance(value, str):
            result[f"{key}_hash"] = hash_email(value, salt)
            result[key] = "[REDACTED]"
        elif key.lower() == "phone" and isinstance(value, str):
            result[key] = mask_phone(value)
        elif isinstance(value, dict):
            result[key] = redact_pii(value, salt)
        elif isinstance(value, list):
            result[key] = [
                redact_pii(item, salt) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result

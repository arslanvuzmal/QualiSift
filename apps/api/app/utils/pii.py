"""
PII (Personally Identifiable Information) redaction utilities.

This module provides functions for hashing emails, masking phone numbers,
and recursively redacting PII from data structures.
"""

import hashlib
import re
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
    Mask a phone number by replacing middle digits with 'X'.

    Handles various phone formats including international codes.
    Examples:
        +1-555-123-4567 -> +1-555-XXX-4567
        5551234567 -> 555XXX4567
        +44 20 7946 0958 -> +44 20 7946 XXXX

    Args:
        phone: The phone number to mask.

    Returns:
        str: The masked phone number with middle digits replaced by 'X'.
    """
    # Extract only digits and leading '+' if present
    has_plus = phone.startswith("+")
    digits_only = re.sub(r"[^\d]", "", phone)

    if len(digits_only) < 4:
        # Too short to mask meaningfully, return as-is with X replacement
        logger.warning("Phone number too short to mask properly", phone_length=len(digits_only))
        return "X" * len(digits_only) if digits_only else phone

    # Keep first 3 and last 4 digits, mask the rest
    keep_start = 3
    keep_end = 4

    if len(digits_only) <= keep_start + keep_end:
        # Not enough digits, mask half
        mask_count = len(digits_only) // 2
        return (
            ("+" if has_plus else "")
            + digits_only[:mask_count]
            + "X" * (len(digits_only) - mask_count)
        )

    unmasked_digits = digits_only[:keep_start] + digits_only[-keep_end:]
    masked_middle = "X" * (len(digits_only) - keep_start - keep_end)

    # Reconstruct with original formatting where possible
    result = digits_only[:keep_start] + masked_middle + digits_only[-keep_end:]

    if has_plus:
        result = "+" + result

    return result


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

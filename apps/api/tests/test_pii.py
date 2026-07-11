"""
Unit tests for PII redaction utilities.
"""


from app.utils.pii import hash_email, mask_phone, redact_pii


class TestHashEmail:
    """Tests for the hash_email function."""

    def test_same_email_same_salt_same_hash(self) -> None:
        """Test that same email with same salt produces same hash."""
        email = "test@example.com"
        salt = "test-salt"
        hash1 = hash_email(email, salt)
        hash2 = hash_email(email, salt)
        assert hash1 == hash2

    def test_same_email_different_salt_different_hash(self) -> None:
        """Test that same email with different salts produces different hashes."""
        email = "test@example.com"
        hash1 = hash_email(email, "salt1")
        hash2 = hash_email(email, "salt2")
        assert hash1 != hash2

    def test_different_emails_different_hashes(self) -> None:
        """Test that different emails produce different hashes."""
        salt = "test-salt"
        hash1 = hash_email("user1@example.com", salt)
        hash2 = hash_email("user2@example.com", salt)
        assert hash1 != hash2

    def test_email_normalization_case_insensitive(self) -> None:
        """Test that email hashing is case-insensitive."""
        salt = "test-salt"
        hash1 = hash_email("Test@Example.com", salt)
        hash2 = hash_email("test@example.com", salt)
        assert hash1 == hash2

    def test_email_normalization_strips_whitespace(self) -> None:
        """Test that email hashing strips whitespace."""
        salt = "test-salt"
        hash1 = hash_email("  test@example.com  ", salt)
        hash2 = hash_email("test@example.com", salt)
        assert hash1 == hash2

    def test_hash_is_hexadecimal(self) -> None:
        """Test that the hash output is valid hexadecimal."""
        hash_value = hash_email("test@example.com", "salt")
        # Should not raise an exception
        int(hash_value, 16)

    def test_hash_length_is_64_chars(self) -> None:
        """Test that SHA-256 hash is 64 characters (256 bits in hex)."""
        hash_value = hash_email("test@example.com", "salt")
        assert len(hash_value) == 64


class TestMaskPhone:
    """Tests for the mask_phone function."""

    def test_mask_us_standard_format(self) -> None:
        """Test masking US standard format +1-555-123-4567."""
        result = mask_phone("+1-555-123-4567")
        assert result.startswith("+1-555-")
        assert result.endswith("4567")
        assert "X" in result

    def test_mask_plain_digits(self) -> None:
        """Test masking plain digit string 5551234567."""
        result = mask_phone("5551234567")
        assert result.startswith("555")
        assert result.endswith("4567")
        assert "X" in result

    def test_mask_international_uk_format(self) -> None:
        """Test masking UK format +44 20 7946 0958."""
        result = mask_phone("+44 20 7946 0958")
        assert result.startswith("+")
        assert "X" in result

    def test_mask_short_number(self) -> None:
        """Test masking short phone numbers."""
        result = mask_phone("12345")
        assert "X" in result
        assert len(result) == 5

    def test_mask_preserves_plus_sign(self) -> None:
        """Test that international plus sign is preserved."""
        result = mask_phone("+1-555-123-4567")
        assert result.startswith("+")

    def test_mask_no_plus_sign_for_local(self) -> None:
        """Test that local numbers don't get a plus sign."""
        result = mask_phone("555-123-4567")
        assert not result.startswith("+")

    def test_mask_very_short_number(self) -> None:
        """Test masking very short numbers (edge case)."""
        result = mask_phone("123")
        assert result == "XXX"


class TestRedactPii:
    """Tests for the redact_pii function."""

    def test_redact_email_field(self) -> None:
        """Test that email fields are hashed and redacted."""
        data = {"email": "user@example.com", "name": "John"}
        result = redact_pii(data, salt="test-salt")
        assert result["email"] == "[REDACTED]"
        assert "email_hash" in result
        assert len(result["email_hash"]) == 64

    def test_redact_phone_field(self) -> None:
        """Test that phone fields are masked."""
        data = {"phone": "+1-555-123-4567", "name": "John"}
        result = redact_pii(data)
        assert "X" in result["phone"]

    def test_redact_nested_dict(self) -> None:
        """Test recursive redaction in nested dictionaries."""
        data = {
            "user": {"email": "nested@example.com"},
            "name": "John",
        }
        result = redact_pii(data, salt="test-salt")
        assert result["user"]["email"] == "[REDACTED]"
        assert "email_hash" in result["user"]

    def test_redact_list_of_dicts(self) -> None:
        """Test redaction in lists containing dictionaries."""
        data = {
            "contacts": [
                {"email": "user1@example.com"},
                {"email": "user2@example.com"},
            ]
        }
        result = redact_pii(data, salt="test-salt")
        assert result["contacts"][0]["email"] == "[REDACTED]"
        assert result["contacts"][1]["email"] == "[REDACTED]"

    def test_non_dict_input_returned_as_is(self) -> None:
        """Test that non-dict input is returned unchanged."""
        result = redact_pii("not a dict")  # type: ignore
        assert result == "not a dict"

    def test_empty_dict_returned_as_is(self) -> None:
        """Test that empty dict is handled correctly."""
        result = redact_pii({})
        assert result == {}

    def test_case_insensitive_email_key(self) -> None:
        """Test that email key matching is case-insensitive."""
        data = {"EMAIL": "user@example.com"}
        result = redact_pii(data, salt="test-salt")
        assert result["EMAIL"] == "[REDACTED]"

    def test_case_insensitive_phone_key(self) -> None:
        """Test that phone key matching is case-insensitive."""
        data = {"PHONE": "+1-555-123-4567"}
        result = redact_pii(data)
        assert "X" in result["PHONE"]

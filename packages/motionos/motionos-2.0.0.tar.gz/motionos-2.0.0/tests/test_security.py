"""
Unit tests for security validation.
"""

import pytest
from motionos.security import validate_api_key, validate_operation, ApiKeyType


class TestAPIKeyValidation:
    """Test API key validation."""

    def test_validate_secret_key(self):
        """Test validation of secret key."""
        is_valid, key_type, error = validate_api_key("sb_secret_abc123")
        assert is_valid is True
        assert key_type == "secret"
        assert error is None

    def test_validate_publishable_key(self):
        """Test validation of publishable key."""
        is_valid, key_type, error = validate_api_key("sb_publishable_abc123")
        assert is_valid is True
        assert key_type == "publishable"
        assert error is None

    def test_validate_invalid_key(self):
        """Test validation of invalid key."""
        is_valid, key_type, error = validate_api_key("invalid_key")
        assert is_valid is False
        assert key_type == "unknown"
        assert error is not None

    def test_validate_empty_key(self):
        """Test validation of empty key."""
        is_valid, key_type, error = validate_api_key("")
        assert is_valid is False
        assert key_type == "unknown"


class TestOperationValidation:
    """Test operation validation."""

    def test_ingest_with_secret_key(self):
        """Test ingest operation with secret key."""
        is_allowed, error = validate_operation("ingest", "secret")
        assert is_allowed is True
        assert error is None

    def test_ingest_with_publishable_key(self):
        """Test ingest operation with publishable key."""
        is_allowed, error = validate_operation("ingest", "publishable")
        assert is_allowed is False
        assert "read-only" in (error or "")

    def test_retrieve_with_any_key(self):
        """Test retrieve operation with any key type."""
        is_allowed, error = validate_operation("retrieve", "secret")
        assert is_allowed is True
        is_allowed, error = validate_operation("retrieve", "publishable")
        assert is_allowed is True


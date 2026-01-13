"""
Unit tests for error handling.
"""

import pytest
from motionos.errors import (
    MotionOSError,
    InvalidAPIKeyError,
    ProjectMismatchError,
    RateLimitError,
    NetworkError,
    TimeoutError,
    EngineUnavailableError,
    InvalidRequestError,
    ForbiddenError,
    NotFoundError,
    create_motionos_error,
    is_retryable,
)


class TestErrorClasses:
    """Test error class hierarchy."""

    def test_motionos_error_base(self):
        """Test base MotionOSError."""
        error = MotionOSError("Test error", "test_code", 400)
        assert str(error) == "MotionOSError: Test error (test_code) - HTTP 400"
        assert error.code == "test_code"
        assert error.http_status == 400

    def test_invalid_api_key_error(self):
        """Test InvalidAPIKeyError."""
        error = InvalidAPIKeyError("Invalid key")
        assert error.code == "invalid_api_key"

    def test_is_retryable(self):
        """Test is_retryable function."""
        retryable_error = NetworkError("Network error")
        non_retryable_error = InvalidRequestError("Invalid request")

        assert is_retryable(retryable_error) is True
        assert is_retryable(non_retryable_error) is False
        assert is_retryable(ValueError("Not a MotionOS error")) is False


class TestErrorCreation:
    """Test error creation from various sources."""

    def test_create_from_dict(self):
        """Test creating error from dict response."""
        error_data = {
            "error": "rate_limited",
            "message": "Rate limit exceeded",
            "request_id": "req-123",
        }
        error = create_motionos_error(error_data)
        assert isinstance(error, RateLimitError)
        assert error.request_id == "req-123"

    def test_create_from_string(self):
        """Test creating error from string."""
        error = create_motionos_error("Test error", "invalid_request")
        assert isinstance(error, MotionOSError)
        assert error.message == "Test error"


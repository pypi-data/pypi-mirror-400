"""Tests for exception classes."""

from changecrab.exceptions import (
    AuthenticationError,
    ChangeCrabError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestChangeCrabError:
    """Test base exception class."""

    def test_init(self):
        """Test exception initialization."""
        error = ChangeCrabError("Test error", status_code=400)
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.response_data == {}

    def test_str_with_status_code(self):
        """Test string representation with status code."""
        error = ChangeCrabError("Test error", status_code=404)
        assert "[404] Test error" in str(error)

    def test_str_without_status_code(self):
        """Test string representation without status code."""
        error = ChangeCrabError("Test error")
        assert str(error) == "Test error"


class TestAuthenticationError:
    """Test AuthenticationError."""

    def test_inheritance(self):
        """Test that AuthenticationError inherits from ChangeCrabError."""
        error = AuthenticationError("Auth failed")
        assert isinstance(error, ChangeCrabError)


class TestNotFoundError:
    """Test NotFoundError."""

    def test_inheritance(self):
        """Test that NotFoundError inherits from ChangeCrabError."""
        error = NotFoundError("Not found")
        assert isinstance(error, ChangeCrabError)


class TestValidationError:
    """Test ValidationError."""

    def test_init_with_errors(self):
        """Test ValidationError with field errors."""
        errors = {"name": ["Required"], "email": ["Invalid format"]}
        error = ValidationError("Validation failed", errors=errors)

        assert error.errors == errors
        assert "name" in str(error)
        assert "email" in str(error)

    def test_str_without_errors(self):
        """Test ValidationError string without field errors."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"


class TestRateLimitError:
    """Test RateLimitError."""

    def test_inheritance(self):
        """Test that RateLimitError inherits from ChangeCrabError."""
        error = RateLimitError("Rate limited")
        assert isinstance(error, ChangeCrabError)


class TestServerError:
    """Test ServerError."""

    def test_inheritance(self):
        """Test that ServerError inherits from ChangeCrabError."""
        error = ServerError("Server error")
        assert isinstance(error, ChangeCrabError)


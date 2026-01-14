"""Tests for exception classes."""

from cryptopanic.exceptions import (
    CryptoPanicAPIError,
    CryptoPanicAuthenticationError,
    CryptoPanicForbiddenError,
    CryptoPanicRateLimitError,
    CryptoPanicServerError,
)


class TestCryptoPanicAPIError:
    """Test the base CryptoPanicAPIError exception."""

    def test_init_with_message(self):
        """Test initialization with just a message."""
        error = CryptoPanicAPIError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code is None
        assert error.response is None

    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        response = {"error": "Something went wrong"}
        error = CryptoPanicAPIError("Test error", status_code=400, response=response)
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.response == response


class TestCryptoPanicAuthenticationError:
    """Test CryptoPanicAuthenticationError."""

    def test_default_message(self):
        """Test default error message."""
        error = CryptoPanicAuthenticationError()
        assert error.status_code == 401
        assert "auth_token" in error.message.lower()

    def test_custom_message(self):
        """Test custom error message."""
        error = CryptoPanicAuthenticationError("Custom auth error")
        assert error.message == "Custom auth error"
        assert error.status_code == 401

    def test_with_response(self):
        """Test error with response data."""
        response = {"detail": "Invalid token"}
        error = CryptoPanicAuthenticationError(response=response)
        assert error.response == response


class TestCryptoPanicForbiddenError:
    """Test CryptoPanicForbiddenError."""

    def test_default_message(self):
        """Test default error message."""
        error = CryptoPanicForbiddenError()
        assert error.status_code == 403

    def test_custom_message(self):
        """Test custom error message."""
        error = CryptoPanicForbiddenError("Custom forbidden error")
        assert error.message == "Custom forbidden error"
        assert error.status_code == 403


class TestCryptoPanicRateLimitError:
    """Test CryptoPanicRateLimitError."""

    def test_default_message(self):
        """Test default error message."""
        error = CryptoPanicRateLimitError()
        assert error.status_code == 429
        assert "rate limit" in error.message.lower()

    def test_custom_message(self):
        """Test custom error message."""
        error = CryptoPanicRateLimitError("Too many requests")
        assert error.message == "Too many requests"
        assert error.status_code == 429


class TestCryptoPanicServerError:
    """Test CryptoPanicServerError."""

    def test_default_message(self):
        """Test default error message."""
        error = CryptoPanicServerError()
        assert error.status_code == 500
        assert "server" in error.message.lower()

    def test_custom_message(self):
        """Test custom error message."""
        error = CryptoPanicServerError("Server is down")
        assert error.message == "Server is down"
        assert error.status_code == 500

"""Custom exceptions for the CryptoPanic API client."""


class CryptoPanicAPIError(Exception):
    """Base exception for all CryptoPanic API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code if available
            response: Full API response if available
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class CryptoPanicAuthenticationError(CryptoPanicAPIError):
    """Raised when authentication fails (401 Unauthorized)."""

    def __init__(
        self, message: str = "Invalid or missing auth_token", response: dict | None = None
    ):
        """Initialize the authentication error."""
        super().__init__(message, status_code=401, response=response)


class CryptoPanicForbiddenError(CryptoPanicAPIError):
    """Raised when access is forbidden (403 Forbidden).

    This can occur due to:
    - Rate limit exceeded
    - No access to the requested endpoint
    """

    def __init__(
        self,
        message: str = "Forbidden - Rate limit exceeded or no access to this endpoint",
        response: dict | None = None,
    ):
        """Initialize the forbidden error."""
        super().__init__(message, status_code=403, response=response)


class CryptoPanicRateLimitError(CryptoPanicAPIError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""

    def __init__(self, message: str = "Rate limit exceeded", response: dict | None = None):
        """Initialize the rate limit error."""
        super().__init__(message, status_code=429, response=response)


class CryptoPanicServerError(CryptoPanicAPIError):
    """Raised when the server returns an error (500 Internal Server Error)."""

    def __init__(self, message: str = "Internal Server Error", response: dict | None = None):
        """Initialize the server error."""
        super().__init__(message, status_code=500, response=response)

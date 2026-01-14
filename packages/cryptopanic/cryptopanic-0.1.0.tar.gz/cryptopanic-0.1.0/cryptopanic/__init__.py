"""CryptoPanic API Python Client Library."""

from cryptopanic.client import CryptoPanicClient
from cryptopanic.exceptions import (
    CryptoPanicAPIError,
    CryptoPanicAuthenticationError,
    CryptoPanicForbiddenError,
    CryptoPanicRateLimitError,
    CryptoPanicServerError,
)

__version__ = "0.1.0"

__all__ = [
    "CryptoPanicClient",
    "CryptoPanicAPIError",
    "CryptoPanicAuthenticationError",
    "CryptoPanicForbiddenError",
    "CryptoPanicRateLimitError",
    "CryptoPanicServerError",
]

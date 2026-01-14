"""Integration tests for the CryptoPanic API.

These tests make real API calls and require a valid CRYPTOPANIC_AUTH_TOKEN
environment variable. They are skipped if the token is not available.

To run integration tests:
    CRYPTOPANIC_AUTH_TOKEN=your_token pytest tests/test_integration.py

Note: Integration tests are not run by default in CI to avoid rate limiting.
"""

import os

import pytest

from cryptopanic import CryptoPanicClient

# Skip all integration tests if token is not available
pytestmark = pytest.mark.skipif(
    not os.getenv("CRYPTOPANIC_AUTH_TOKEN"),
    reason="CRYPTOPANIC_AUTH_TOKEN not set - skipping integration tests",
)


@pytest.mark.integration
class TestCryptoPanicClientIntegration:
    """Integration tests that make real API calls."""

    @pytest.fixture
    def client(self, auth_token):
        """Create a client instance with auth token from environment."""
        return CryptoPanicClient(auth_token=auth_token)

    def test_get_posts_basic(self, client):
        """Test getting posts with basic parameters."""
        posts = client.get_posts()
        assert posts is not None
        assert hasattr(posts, "results")
        assert hasattr(posts, "next")
        assert hasattr(posts, "previous")

    def test_get_posts_with_currencies(self, client):
        """Test getting posts filtered by currencies."""
        posts = client.get_posts(currencies=["BTC"])
        assert posts is not None
        # Results may be empty, but response should be valid
        assert isinstance(posts.results, list)

    def test_get_posts_with_filter(self, client):
        """Test getting posts with filter."""
        posts = client.get_posts(filter="hot")
        assert posts is not None
        assert isinstance(posts.results, list)

    def test_get_posts_public_mode(self, client):
        """Test getting posts in public mode."""
        posts = client.get_posts(public=True, regions=["en"])
        assert posts is not None
        assert isinstance(posts.results, list)

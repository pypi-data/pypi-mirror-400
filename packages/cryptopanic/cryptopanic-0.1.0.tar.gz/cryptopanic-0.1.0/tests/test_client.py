"""Tests for the CryptoPanic client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from cryptopanic.client import CryptoPanicClient
from cryptopanic.exceptions import (
    CryptoPanicAPIError,
    CryptoPanicAuthenticationError,
    CryptoPanicForbiddenError,
    CryptoPanicRateLimitError,
    CryptoPanicServerError,
)
from cryptopanic.models import PortfolioResponse, PostsResponse


class TestCryptoPanicClientInit:
    """Test CryptoPanicClient initialization."""

    def test_init_with_token(self):
        """Test initialization with auth token."""
        client = CryptoPanicClient(auth_token="test_token")
        assert client.auth_token == "test_token"
        assert client.timeout == 30

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout."""
        client = CryptoPanicClient(auth_token="test_token", timeout=60)
        assert client.timeout == 60

    def test_init_with_empty_token(self):
        """Test initialization fails with empty token."""
        with pytest.raises(ValueError, match="auth_token is required"):
            CryptoPanicClient(auth_token="")

    def test_init_with_none_token(self):
        """Test initialization fails with None token."""
        with pytest.raises(ValueError, match="auth_token is required"):
            CryptoPanicClient(auth_token=None)  # type: ignore[arg-type]


class TestCryptoPanicClientMakeRequest:
    """Test the _make_request method."""

    @patch("cryptopanic.client.requests.Session")
    def test_successful_request(self, mock_session_class):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "next": None, "previous": None}
        mock_response.content = b'{"results": [], "next": null, "previous": null}'
        mock_response.raise_for_status = Mock()

        mock_session = Mock()
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        client = CryptoPanicClient(auth_token="test_token")
        result = client._make_request("/posts/", params={"filter": "rising"})

        assert "results" in result
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["params"]["auth_token"] == "test_token"
        assert call_args[1]["params"]["filter"] == "rising"

    @patch("cryptopanic.client.requests.Session")
    def test_request_with_401_error(self, mock_session_class):
        """Test request with 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.content = b'{"error": "Invalid token"}'
        mock_response.json.return_value = {"error": "Invalid token"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        mock_session = Mock()
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(CryptoPanicAuthenticationError) as exc_info:
            client._make_request("/posts/")

        assert exc_info.value.status_code == 401

    @patch("cryptopanic.client.requests.Session")
    def test_request_with_403_error(self, mock_session_class):
        """Test request with 403 forbidden error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.content = b'{"error": "Forbidden"}'
        mock_response.json.return_value = {"error": "Forbidden"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        mock_session = Mock()
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(CryptoPanicForbiddenError) as exc_info:
            client._make_request("/posts/")

        assert exc_info.value.status_code == 403

    @patch("cryptopanic.client.requests.Session")
    def test_request_with_429_error(self, mock_session_class):
        """Test request with 429 rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.content = b'{"error": "Rate limit exceeded"}'
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        mock_session = Mock()
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(CryptoPanicRateLimitError) as exc_info:
            client._make_request("/posts/")

        assert exc_info.value.status_code == 429

    @patch("cryptopanic.client.requests.Session")
    def test_request_with_500_error(self, mock_session_class):
        """Test request with 500 server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.content = b'{"error": "Internal server error"}'
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        mock_session = Mock()
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(CryptoPanicServerError) as exc_info:
            client._make_request("/posts/")

        assert exc_info.value.status_code == 500

    @patch("cryptopanic.client.requests.Session")
    def test_request_network_error(self, mock_session_class):
        """Test request with network error."""
        mock_session = Mock()
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(CryptoPanicAPIError) as exc_info:
            client._make_request("/posts/")

        assert "Network error" in str(exc_info.value)


class TestCryptoPanicClientGetPosts:
    """Test the get_posts method."""

    @patch("cryptopanic.client.CryptoPanicClient._make_request")
    def test_get_posts_basic(self, mock_make_request):
        """Test basic get_posts call."""
        mock_make_request.return_value = {
            "results": [],
            "next": None,
            "previous": None,
        }

        client = CryptoPanicClient(auth_token="test_token")
        response = client.get_posts()

        assert isinstance(response, PostsResponse)
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[0][0] == "/posts/"

    @patch("cryptopanic.client.CryptoPanicClient._make_request")
    def test_get_posts_with_currencies(self, mock_make_request):
        """Test get_posts with currencies filter."""
        mock_make_request.return_value = {
            "results": [],
            "next": None,
            "previous": None,
        }

        client = CryptoPanicClient(auth_token="test_token")
        client.get_posts(currencies=["BTC", "ETH"])

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["currencies"] == "BTC,ETH"

    @patch("cryptopanic.client.CryptoPanicClient._make_request")
    def test_get_posts_with_filter(self, mock_make_request):
        """Test get_posts with filter."""
        mock_make_request.return_value = {
            "results": [],
            "next": None,
            "previous": None,
        }

        client = CryptoPanicClient(auth_token="test_token")
        client.get_posts(filter="rising")

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["filter"] == "rising"

    def test_get_posts_invalid_filter(self):
        """Test get_posts with invalid filter."""
        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(ValueError, match="filter must be one of"):
            client.get_posts(filter="invalid")

    def test_get_posts_invalid_kind(self):
        """Test get_posts with invalid kind."""
        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(ValueError, match="kind must be one of"):
            client.get_posts(kind="invalid")

    def test_get_posts_invalid_size(self):
        """Test get_posts with invalid size."""
        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(ValueError, match="size must be between"):
            client.get_posts(size=1000)

    def test_get_posts_panic_sort_without_period(self):
        """Test get_posts with panic_sort but no panic_period."""
        client = CryptoPanicClient(auth_token="test_token")
        with pytest.raises(ValueError, match="panic_sort requires panic_period"):
            client.get_posts(panic_sort="desc")

    @patch("cryptopanic.client.CryptoPanicClient._make_request")
    def test_get_posts_with_last_pull_datetime(self, mock_make_request):
        """Test get_posts with datetime object for last_pull."""
        mock_make_request.return_value = {
            "results": [],
            "next": None,
            "previous": None,
        }

        client = CryptoPanicClient(auth_token="test_token")
        dt = datetime(2024, 1, 1, 12, 0, 0)
        client.get_posts(last_pull=dt)

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert "last_pull" in params
        assert params["last_pull"] == dt.isoformat()

    @patch("cryptopanic.client.CryptoPanicClient._make_request")
    def test_get_posts_with_public_mode(self, mock_make_request):
        """Test get_posts with public mode."""
        mock_make_request.return_value = {
            "results": [],
            "next": None,
            "previous": None,
        }

        client = CryptoPanicClient(auth_token="test_token")
        client.get_posts(public=True)

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["public"] == "true"

    @patch("cryptopanic.client.CryptoPanicClient._make_request")
    def test_get_posts_with_regions(self, mock_make_request):
        """Test get_posts with regions filter."""
        mock_make_request.return_value = {
            "results": [],
            "next": None,
            "previous": None,
        }

        client = CryptoPanicClient(auth_token="test_token")
        client.get_posts(regions=["en", "fr"])

        call_args = mock_make_request.call_args
        params = call_args[1]["params"]
        assert params["regions"] == "en,fr"


class TestCryptoPanicClientGetPortfolio:
    """Test the get_portfolio method."""

    @patch("cryptopanic.client.CryptoPanicClient._make_request")
    def test_get_portfolio(self, mock_make_request):
        """Test get_portfolio call."""
        mock_make_request.return_value = {}

        client = CryptoPanicClient(auth_token="test_token")
        response = client.get_portfolio()

        assert isinstance(response, PortfolioResponse)
        mock_make_request.assert_called_once_with("/portfolio/")

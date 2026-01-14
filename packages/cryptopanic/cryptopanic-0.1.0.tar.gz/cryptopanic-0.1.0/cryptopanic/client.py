"""Main client for interacting with the CryptoPanic API."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

import requests

from cryptopanic.exceptions import (
    CryptoPanicAPIError,
    CryptoPanicAuthenticationError,
    CryptoPanicForbiddenError,
    CryptoPanicRateLimitError,
    CryptoPanicServerError,
)
from cryptopanic.models import PortfolioResponse, PostsResponse

if TYPE_CHECKING:
    pass  # Reserved for future type-only imports


class CryptoPanicClient:
    """Client for interacting with the CryptoPanic API.

    Example:
        ```python
        from cryptopanic import CryptoPanicClient

        client = CryptoPanicClient(auth_token="your_token")
        posts = client.get_posts(currencies=["BTC", "ETH"], filter="rising")
        ```
    """

    BASE_URL = "https://cryptopanic.com/api/developer/v2"

    def __init__(self, auth_token: str, timeout: int = 30):
        """Initialize the CryptoPanic client.

        Args:
            auth_token: Your CryptoPanic API authentication token
            timeout: Request timeout in seconds (default: 30)

        Raises:
            ValueError: If auth_token is empty or None
        """
        if not auth_token:
            raise ValueError("auth_token is required and cannot be empty")

        self.auth_token = auth_token
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "cryptopanic-python/0.1.0"})

    def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        method: str = "GET",
    ) -> dict[str, Any]:
        """Make a request to the CryptoPanic API.

        Args:
            endpoint: API endpoint (e.g., '/posts/')
            params: Query parameters
            method: HTTP method (default: 'GET')

        Returns:
            JSON response as a dictionary

        Raises:
            CryptoPanicAuthenticationError: If authentication fails (401)
            CryptoPanicForbiddenError: If access is forbidden (403)
            CryptoPanicRateLimitError: If rate limit is exceeded (429)
            CryptoPanicServerError: If server error occurs (500)
            CryptoPanicAPIError: For other API errors
            requests.RequestException: For network errors
        """
        if params is None:
            params = {}

        # Always include auth_token
        params["auth_token"] = self.auth_token

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.request(
                method=method, url=url, params=params, timeout=self.timeout
            )
            response.raise_for_status()

            # Handle empty responses
            if not response.content:
                return {}

            return response.json()  # type: ignore[no-any-return]

        except requests.exceptions.HTTPError as e:
            error_response = None
            try:
                error_response = e.response.json() if e.response.content else None
            except (ValueError, AttributeError):
                pass

            status_code = e.response.status_code if e.response else None

            if status_code == 401:
                raise CryptoPanicAuthenticationError(
                    "Invalid or missing auth_token",
                    response=error_response,
                ) from e
            elif status_code == 403:
                raise CryptoPanicForbiddenError(
                    "Forbidden - Rate limit exceeded or no access to this endpoint",
                    response=error_response,
                ) from e
            elif status_code == 429:
                raise CryptoPanicRateLimitError(
                    "Rate limit exceeded",
                    response=error_response,
                ) from e
            elif status_code == 500:
                raise CryptoPanicServerError(
                    "Internal Server Error",
                    response=error_response,
                ) from e
            else:
                raise CryptoPanicAPIError(
                    f"API request failed: {e}",
                    status_code=status_code,
                    response=error_response,
                ) from e

        except requests.exceptions.RequestException as e:
            raise CryptoPanicAPIError(f"Network error: {e}") from e

    def get_posts(
        self,
        public: bool | None = None,
        currencies: list[str] | None = None,
        regions: list[str] | None = None,
        filter: str | None = None,  # noqa: A002
        kind: str | None = None,
        following: bool | None = None,
        last_pull: datetime | str | None = None,
        panic_period: str | None = None,
        panic_sort: str | None = None,
        size: int | None = None,
        with_content: bool | None = None,
        search: str | None = None,
        format: str | None = None,  # noqa: A002
    ) -> PostsResponse:
        """Retrieve a list of news posts.

        Args:
            public: Enable public mode (uses non-user-specific settings)
            currencies: Filter by currency codes (e.g., ['BTC', 'ETH'])
            regions: Filter by regions (e.g., ['en', 'fr'])
            filter: Filter by type: 'rising', 'hot', 'bullish', 'bearish', 'important', 'saved', 'lol'
            kind: Filter by news kind: 'news', 'media', 'all' (default: 'all')
            following: Filter by sources you follow (PRIVATE API only)
            last_pull: Limit search to last pull time (ISO 8601 string or datetime) - Enterprise only
            panic_period: Include panic score for period: '1h', '6h', '24h' - Enterprise only
            panic_sort: Sort by panic score: 'asc' or 'desc' (requires panic_period) - Enterprise only
            size: Items per page (1-500, max 500) - Enterprise only
            with_content: Filter items with full content - Enterprise only
            search: Search by keyword - Enterprise only
            format: Response format (e.g., 'rss') - returns max 20 items

        Returns:
            PostsResponse containing list of posts and pagination info

        Raises:
            CryptoPanicAPIError: For API errors
            ValueError: For invalid parameter combinations

        Example:
            ```python
            # Get rising news for BTC and ETH
            posts = client.get_posts(
                currencies=['BTC', 'ETH'],
                filter='rising'
            )

            # Get public news in English
            posts = client.get_posts(
                public=True,
                regions=['en']
            )
            ```
        """
        params: dict[str, Any] = {}

        if public is not None:
            params["public"] = "true" if public else "false"

        if currencies:
            params["currencies"] = ",".join(currencies)

        if regions:
            params["regions"] = ",".join(regions)

        if filter:
            valid_filters = {"rising", "hot", "bullish", "bearish", "important", "saved", "lol"}
            if filter not in valid_filters:
                raise ValueError(f"filter must be one of {valid_filters}, got: {filter}")
            params["filter"] = filter

        if kind:
            valid_kinds = {"news", "media", "all"}
            if kind not in valid_kinds:
                raise ValueError(f"kind must be one of {valid_kinds}, got: {kind}")
            params["kind"] = kind

        if following is not None:
            params["following"] = "true" if following else "false"

        if last_pull:
            if isinstance(last_pull, datetime):
                params["last_pull"] = last_pull.isoformat()
            else:
                params["last_pull"] = last_pull

        if panic_period:
            valid_periods = {"1h", "6h", "24h"}
            if panic_period not in valid_periods:
                raise ValueError(
                    f"panic_period must be one of {valid_periods}, got: {panic_period}"
                )
            params["panic_period"] = panic_period

        if panic_sort:
            if not panic_period:
                raise ValueError("panic_sort requires panic_period to be set")
            valid_sorts = {"asc", "desc"}
            if panic_sort not in valid_sorts:
                raise ValueError(f"panic_sort must be one of {valid_sorts}, got: {panic_sort}")
            params["panic_sort"] = panic_sort

        if size is not None:
            if not (1 <= size <= 500):
                raise ValueError("size must be between 1 and 500")
            params["size"] = str(size)

        if with_content is not None:
            params["with_content"] = "true" if with_content else "false"

        if search:
            params["search"] = search

        if format:
            params["format"] = format

        response_data = self._make_request("/posts/", params=params)
        return PostsResponse(**response_data)

    def get_portfolio(self) -> PortfolioResponse:
        """Retrieve your portfolio.

        Note:
            Available only for GROWTH and ENTERPRISE API plans.

        Returns:
            PortfolioResponse containing portfolio data

        Raises:
            CryptoPanicAPIError: For API errors
            CryptoPanicForbiddenError: If your plan doesn't have access

        Example:
            ```python
            portfolio = client.get_portfolio()
            ```
        """
        response_data = self._make_request("/portfolio/")
        return PortfolioResponse(**response_data)

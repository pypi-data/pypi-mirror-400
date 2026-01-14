"""Data models for CryptoPanic API responses."""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

if TYPE_CHECKING:
    pass


class Instrument(BaseModel):
    """Represents a cryptocurrency instrument."""

    code: str = Field(..., description="Ticker or code of the instrument")
    title: str = Field(..., description="Full name of the instrument")
    slug: str = Field(..., description="URL-friendly identifier")
    url: HttpUrl = Field(..., description="Link to the instrument's page")
    market_cap_usd: float | None = Field(None, description="Market capitalization in USD")
    price_in_usd: float | None = Field(None, description="Current price in USD")
    price_in_btc: float | None = Field(None, description="Current price in BTC")
    price_in_eth: float | None = Field(None, description="Current price in ETH")
    price_in_eur: float | None = Field(None, description="Current price in EUR")
    market_rank: int | None = Field(None, description="Global market rank of the instrument")


class Source(BaseModel):
    """Represents a news source."""

    title: str = Field(..., description="Publisher name")
    region: str = Field(..., description="Language code (e.g. 'en', 'fr')")
    domain: str = Field(..., description="Publisher's domain")
    type: str = Field(..., description="One of 'feed', 'blog', 'twitter', 'media', 'reddit'")


class Votes(BaseModel):
    """Represents vote counts for a post."""

    negative: int = Field(default=0, description="Count of negative votes")
    positive: int = Field(default=0, description="Count of positive votes")
    important: int = Field(default=0, description="Count of 'important' votes")
    liked: int = Field(default=0, description="Count of 'like' votes")
    disliked: int = Field(default=0, description="Count of 'dislike' votes")
    lol: int = Field(default=0, description="Count of 'lol' reactions")
    toxic: int = Field(default=0, description="Count of 'toxic' reactions")
    saved: int = Field(default=0, description="Count of times post was saved")
    comments: int = Field(default=0, description="Count of comments on the post")


class Content(BaseModel):
    """Represents the content of a post."""

    original: str | None = Field(None, description="Raw HTML/markup of the original article")
    clean: str | None = Field(None, description="Sanitized text-only version of the content")


class Post(BaseModel):
    """Represents a news post from CryptoPanic."""

    id: int = Field(..., description="Unique identifier for the post")
    slug: str = Field(..., description="URL-friendly short title")
    title: str = Field(..., description="Full title of the post")
    description: str | None = Field(None, description="Short summary or excerpt")
    published_at: datetime = Field(..., description="When the post was published (ISO 8601)")
    created_at: datetime = Field(..., description="When the post was created in the system")
    kind: str = Field(..., description="Content type: 'news', 'media', 'blog', 'twitter', 'reddit'")
    source: Source | None = Field(None, description="Source information")
    original_url: HttpUrl | None = Field(None, description="Link to the original article")
    url: HttpUrl | None = Field(None, description="Link to the Cryptopanic-hosted article")
    image: HttpUrl | None = Field(None, description="URL of the cover image")
    instruments: list[Instrument] = Field(
        default_factory=list, description="List of instruments mentioned"
    )
    votes: Votes = Field(default_factory=Votes, description="Vote counts")
    panic_score: int | None = Field(None, ge=0, le=100, description="Proprietary score (0-100)")
    panic_score_1h: int | None = Field(
        None, ge=0, le=100, description="Proprietary score within first hour (0-100)"
    )
    author: str | None = Field(None, description="Name of the article's author")
    content: Content | None = Field(None, description="Full content of the post")

    # Pydantic v2 automatically serializes datetime to ISO format
    model_config = ConfigDict()


class PostsResponse(BaseModel):
    """Response model for the posts endpoint."""

    next: str | None = Field(None, description="URL of the next page of results")
    previous: str | None = Field(None, description="URL of the previous page of results")
    results: list[Post] = Field(default_factory=list, description="List of post objects")


class PortfolioItem(BaseModel):
    """Represents a portfolio item (structure depends on API response)."""

    pass  # TODO: Implement when API response structure is known


class PortfolioResponse(BaseModel):
    """Response model for the portfolio endpoint."""

    pass  # TODO: Implement when API response structure is known

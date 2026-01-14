"""Tests for data models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from cryptopanic.models import Content, Instrument, Post, PostsResponse, Source, Votes


class TestInstrument:
    """Test Instrument model."""

    def test_minimal_instrument(self):
        """Test creating an instrument with minimal required fields."""
        instrument = Instrument(
            code="BTC",
            title="Bitcoin",
            slug="bitcoin",
            url="https://cryptopanic.com/api/developer/v2/coins/btc/",
        )
        assert instrument.code == "BTC"
        assert instrument.title == "Bitcoin"
        assert instrument.market_cap_usd is None

    def test_full_instrument(self):
        """Test creating an instrument with all fields."""
        instrument = Instrument(
            code="BTC",
            title="Bitcoin",
            slug="bitcoin",
            url="https://cryptopanic.com/api/developer/v2/coins/btc/",
            market_cap_usd=1000000000.0,
            price_in_usd=50000.0,
            price_in_btc=1.0,
            price_in_eth=10.0,
            price_in_eur=45000.0,
            market_rank=1,
        )
        assert instrument.price_in_usd == 50000.0
        assert instrument.market_rank == 1


class TestSource:
    """Test Source model."""

    def test_source_creation(self):
        """Test creating a source."""
        source = Source(
            title="CoinDesk",
            region="en",
            domain="coindesk.com",
            type="feed",
        )
        assert source.title == "CoinDesk"
        assert source.region == "en"
        assert source.type == "feed"


class TestVotes:
    """Test Votes model."""

    def test_default_votes(self):
        """Test creating votes with defaults."""
        votes = Votes()
        assert votes.negative == 0
        assert votes.positive == 0
        assert votes.comments == 0

    def test_votes_with_values(self):
        """Test creating votes with values."""
        votes = Votes(
            positive=10,
            negative=2,
            important=5,
            comments=3,
        )
        assert votes.positive == 10
        assert votes.negative == 2
        assert votes.important == 5


class TestContent:
    """Test Content model."""

    def test_content_with_clean(self):
        """Test content with clean text."""
        content = Content(clean="This is clean text")
        assert content.clean == "This is clean text"
        assert content.original is None

    def test_content_with_original(self):
        """Test content with original HTML."""
        content = Content(original="<p>HTML content</p>")
        assert content.original == "<p>HTML content</p>"
        assert content.clean is None


class TestPost:
    """Test Post model."""

    def test_minimal_post(self):
        """Test creating a post with minimal required fields."""
        post = Post(
            id=1,
            slug="test-post",
            title="Test Post",
            description="Test description",
            published_at=datetime.now(),
            created_at=datetime.now(),
            kind="news",
            source=Source(
                title="Test Source",
                region="en",
                domain="test.com",
                type="feed",
            ),
            original_url="https://test.com/article",
            url="https://cryptopanic.com/news/1/test-post/",
        )
        assert post.id == 1
        assert post.title == "Test Post"
        assert post.instruments == []
        assert post.votes.positive == 0

    def test_post_with_instruments(self):
        """Test post with instruments."""
        instrument = Instrument(
            code="BTC",
            title="Bitcoin",
            slug="bitcoin",
            url="https://cryptopanic.com/api/developer/v2/coins/btc/",
        )
        post = Post(
            id=1,
            slug="test-post",
            title="Test Post",
            description="Test description",
            published_at=datetime.now(),
            created_at=datetime.now(),
            kind="news",
            source=Source(
                title="Test Source",
                region="en",
                domain="test.com",
                type="feed",
            ),
            original_url="https://test.com/article",
            url="https://cryptopanic.com/news/1/test-post/",
            instruments=[instrument],
        )
        assert len(post.instruments) == 1
        assert post.instruments[0].code == "BTC"

    def test_post_without_optional_fields(self):
        """Test creating a post without optional fields (matching real API responses)."""
        post = Post(
            id=1,
            slug="test-post",
            title="Test Post",
            published_at=datetime.now(),
            created_at=datetime.now(),
            kind="news",
        )
        assert post.id == 1
        assert post.description is None
        assert post.source is None
        assert post.original_url is None
        assert post.url is None

    def test_post_panic_score_validation(self):
        """Test panic score validation (0-100)."""
        post = Post(
            id=1,
            slug="test-post",
            title="Test Post",
            description="Test description",
            published_at=datetime.now(),
            created_at=datetime.now(),
            kind="news",
            source=Source(
                title="Test Source",
                region="en",
                domain="test.com",
                type="feed",
            ),
            original_url="https://test.com/article",
            url="https://cryptopanic.com/news/1/test-post/",
            panic_score=50,
        )
        assert post.panic_score == 50

        # Test invalid panic score
        with pytest.raises(ValidationError):
            Post(
                id=1,
                slug="test-post",
                title="Test Post",
                description="Test description",
                published_at=datetime.now(),
                created_at=datetime.now(),
                kind="news",
                source=Source(
                    title="Test Source",
                    region="en",
                    domain="test.com",
                    type="feed",
                ),
                original_url="https://test.com/article",
                url="https://cryptopanic.com/news/1/test-post/",
                panic_score=150,  # Invalid: > 100
            )


class TestPostsResponse:
    """Test PostsResponse model."""

    def test_empty_response(self):
        """Test empty response."""
        response = PostsResponse()
        assert response.results == []
        assert response.next is None
        assert response.previous is None

    def test_response_with_posts(self):
        """Test response with posts."""
        post = Post(
            id=1,
            slug="test-post",
            title="Test Post",
            description="Test description",
            published_at=datetime.now(),
            created_at=datetime.now(),
            kind="news",
            source=Source(
                title="Test Source",
                region="en",
                domain="test.com",
                type="feed",
            ),
            original_url="https://test.com/article",
            url="https://cryptopanic.com/news/1/test-post/",
        )
        response = PostsResponse(
            results=[post],
            next="https://cryptopanic.com/api/developer/v2/posts/?page=2",
        )
        assert len(response.results) == 1
        assert response.next is not None
        assert response.previous is None

"""Tests for Article data model."""

from datetime import datetime, timezone, timedelta

from src.collect.models import Article


class TestArticle:
    """Article model unit tests."""

    def test_article_creation(self):
        """Create an Article with all fields."""
        art = Article(
            title="Test",
            url="https://example.com",
            source="rss",
            source_name="Test",
            published_at=datetime.now(timezone.utc),
            summary="Summary text",
            categories=["AI"],
            author="Author",
        )
        assert art.title == "Test"
        assert art.url == "https://example.com"
        assert art.source == "rss"
        assert art.categories == ["AI"]

    def test_article_minimal_fields(self):
        """Create an Article with only required fields."""
        art = Article(
            title="Minimal",
            url="https://example.com/min",
            source="newsapi",
            source_name="Min",
        )
        assert art.summary == ""
        assert art.categories == []
        assert art.author == ""
        assert art.published_at is None

    def test_is_recent_within_3_days(self):
        """Article published today should be recent."""
        art = Article(
            title="Recent",
            url="https://example.com/recent",
            source="rss",
            source_name="Test",
            published_at=datetime.now(timezone.utc),
        )
        assert art.is_recent(days=3) is True

    def test_is_recent_older_than_3_days(self):
        """Article published 10 days ago should not be recent."""
        art = Article(
            title="Old",
            url="https://example.com/old",
            source="rss",
            source_name="Test",
            published_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        assert art.is_recent(days=3) is False

    def test_is_recent_no_date(self):
        """Article without published_at should be treated as recent."""
        art = Article(
            title="No date",
            url="https://example.com/no-date",
            source="rss",
            source_name="Test",
        )
        assert art.is_recent() is True

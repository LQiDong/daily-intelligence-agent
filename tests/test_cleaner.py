"""Tests for the Cleaner module."""

from datetime import datetime, timezone, timedelta

from src.collect.models import Article
from src.process.cleaner import Cleaner


class TestCleaner:
    """Cleaner unit tests."""

    def test_clean_empty_list(self):
        """Empty input returns empty list."""
        cleaner = Cleaner()
        assert cleaner.clean([]) == []

    def test_remove_empty_title(self):
        """Articles with empty titles are removed."""
        articles = [
            Article(title="Good Title", url="https://example.com/1", source="rss", source_name="Test"),
            Article(title="", url="https://example.com/2", source="rss", source_name="Test"),
            Article(title="   ", url="https://example.com/3", source="rss", source_name="Test"),
        ]
        cleaned = Cleaner().clean(articles)
        assert len(cleaned) == 1
        assert cleaned[0].title == "Good Title"

    def test_remove_invalid_url(self):
        """Articles with invalid URLs are removed."""
        articles = [
            Article(title="A", url="https://example.com/1", source="rss", source_name="Test"),
            Article(title="B", url="http://example.com/2", source="rss", source_name="Test"),
            Article(title="C", url="", source="rss", source_name="Test"),
            Article(title="D", url="not-a-url", source="rss", source_name="Test"),
            Article(title="E", url="ftp://bad.com", source="rss", source_name="Test"),
        ]
        cleaned = Cleaner().clean(articles)
        assert len(cleaned) == 2
        assert cleaned[0].title == "A"
        assert cleaned[1].title == "B"

    def test_remove_future_date(self):
        """Articles with future dates (>1h ahead) are removed."""
        articles = [
            Article(
                title="Recent", url="https://example.com/1", source="rss", source_name="Test",
                published_at=datetime.now(timezone.utc),
            ),
            Article(
                title="Future", url="https://example.com/2", source="rss", source_name="Test",
                published_at=datetime.now(timezone.utc) + timedelta(days=2),
            ),
            Article(
                title="Old", url="https://example.com/3", source="rss", source_name="Test",
                published_at=datetime.now(timezone.utc) - timedelta(days=10),
            ),
            Article(
                title="No Date", url="https://example.com/4", source="rss", source_name="Test",
            ),
        ]
        cleaned = Cleaner().clean(articles)
        assert len(cleaned) == 2
        titles = {a.title for a in cleaned}
        assert "Recent" in titles
        assert "No Date" in titles

    def test_trim_strings(self):
        """Whitespace is trimmed from string fields."""
        articles = [
            Article(
                title="  Hello World  ",
                url="  https://example.com/x  ",
                source="  rss  ",
                source_name="  Test Source  ",
                summary="  Some summary  ",
                categories=["  AI  ", "  Tech  "],
                author="  Author  ",
            ),
        ]
        cleaned = Cleaner().clean(articles)
        assert cleaned[0].title == "Hello World"
        assert cleaned[0].url == "https://example.com/x"
        assert cleaned[0].source == "rss"
        assert cleaned[0].source_name == "Test Source"
        assert cleaned[0].summary == "Some summary"
        assert cleaned[0].categories == ["AI", "Tech"]
        assert cleaned[0].author == "Author"

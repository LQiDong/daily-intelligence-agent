"""Tests for the Deduper module."""

from src.collect.models import Article
from src.process.deduper import Deduper


def _article(title: str, url: str) -> Article:
    return Article(title=title, url=url, source="rss", source_name="Test")


class TestDeduper:
    """Deduper unit tests."""

    def test_dedup_empty(self):
        """Empty input returns empty list."""
        assert Deduper().deduplicate([]) == []

    def test_dedup_url_identical(self):
        """Articles with identical URLs are deduplicated."""
        articles = [
            _article("First", "https://example.com/a"),
            _article("Second", "https://example.com/a"),  # same URL
            _article("Third", "https://example.com/b"),
        ]
        deduped = Deduper().deduplicate(articles)
        assert len(deduped) == 2
        assert deduped[0].title == "First"
        assert deduped[1].title == "Third"

    def test_dedup_url_trailing_slash(self):
        """URLs differing only by trailing slash are deduplicated."""
        articles = [
            _article("First", "https://example.com/a"),
            _article("Second", "https://example.com/a/"),  # trailing slash
        ]
        deduped = Deduper().deduplicate(articles)
        assert len(deduped) == 1

    def test_dedup_title_similar(self):
        """Very similar titles are deduplicated."""
        articles = [
            _article("Apple Releases New iPhone Model Today", "https://example.com/1"),
            _article("Apple releases new iPhone model today", "https://example.com/2"),
        ]
        deduped = Deduper().deduplicate(articles)
        assert len(deduped) == 1

    def test_dedup_title_different(self):
        """Different titles are not deduplicated."""
        articles = [
            _article("AI Breakthrough in Healthcare Research", "https://example.com/1"),
            _article("Stock Market Hits All-Time High", "https://example.com/2"),
        ]
        deduped = Deduper().deduplicate(articles)
        assert len(deduped) == 2

    def test_dedup_no_duplicates(self):
        """No duplicates → same count."""
        articles = [
            _article("Apple releases new iPhone", "https://example.com/a"),
            _article("Stock market reaches all-time high", "https://example.com/b"),
            _article("Quantum computing breakthrough achieved", "https://example.com/c"),
        ]
        deduped = Deduper().deduplicate(articles)
        assert len(deduped) == 3

    def test_jaccard_similarity(self):
        """Jaccard similarity works correctly."""
        sim = Deduper._jaccard_similarity({"apple", "releases", "iphone"}, {"apple", "releases", "iphone"})
        assert sim == 1.0

        sim = Deduper._jaccard_similarity({"apple", "releases", "iphone"}, {"stock", "market", "high"})
        assert sim == 0.0

        sim = Deduper._jaccard_similarity({"apple", "releases", "iphone"}, {"apple", "releases", "new"})
        assert sim == 0.5

    def test_normalize_removes_stop_words(self):
        """Normalization removes stop words and short words."""
        tokens = Deduper._normalize("The apple releases a new iPhone")
        assert "the" not in tokens
        assert "a" not in tokens
        assert "apple" in tokens
        assert "releases" in tokens
        assert "iphone" in tokens

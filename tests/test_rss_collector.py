"""Tests for RSSCollector with mocked feedparser."""

from unittest.mock import patch, MagicMock

from src.collect.rss_collector import RSSCollector


def _make_entry(**kwargs) -> dict:
    """Build a dict that mimics a feedparser entry (supports both .get() and attr access)."""
    return kwargs


class TestRSSCollector:
    """RSSCollector unit tests."""

    @patch("src.collect.rss_collector.feedparser.parse")
    def test_fetch_success(self, mock_parse):
        """Collector returns articles from feed."""
        entries = [
            _make_entry(
                title="AI Breakthrough",
                link="https://example.com/ai",
                published_parsed=(2026, 6, 10, 12, 0, 0, 2, 161, 0),
                summary="An AI breakthrough article.",
                tags=[],
                author="Author A",
            ),
            _make_entry(
                title="Tech News",
                link="https://example.com/tech",
                published_parsed=(2026, 6, 9, 8, 0, 0, 1, 160, 0),
                summary="Latest tech news.",
                tags=[{"term": "Technology"}],
                author="Author B",
            ),
        ]

        mock_feed = {"title": "Test Feed Title"}
        mock_parse.return_value = MagicMock(
            bozo=False,
            feed=mock_feed,
            entries=entries,
        )

        collector = RSSCollector()
        collector.feeds = ["https://test-feed.example.com/rss"]

        articles = collector.fetch()
        assert len(articles) == 2
        assert articles[0].title == "AI Breakthrough"
        assert articles[0].source == "rss"
        assert articles[0].source_name == "Test Feed Title"
        assert articles[1].categories == ["Technology"]

    @patch("src.collect.rss_collector.feedparser.parse")
    def test_fetch_parse_error(self, mock_parse):
        """Bozo feed without entries raises error and is caught."""
        mock_parse.return_value = MagicMock(
            bozo=True,
            bozo_exception=Exception("Parse error"),
            entries=[],
        )

        collector = RSSCollector()
        collector.feeds = ["https://bad-feed.example.com/rss"]

        articles = collector.fetch()
        assert articles == []

    @patch("src.collect.rss_collector.feedparser.parse")
    def test_fetch_empty_feed(self, mock_parse):
        """Empty feed returns empty list."""
        mock_parse.return_value = MagicMock(
            bozo=False,
            feed={"title": "Empty Feed"},
            entries=[],
        )
        collector = RSSCollector()
        collector.feeds = ["https://empty.example.com/rss"]

        articles = collector.fetch()
        assert articles == []

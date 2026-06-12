"""Integration tests for the NewsCollector orchestrator."""

from unittest.mock import patch, MagicMock

from src.collect.collector import NewsCollector
from src.collect.models import Article


class TestNewsCollector:
    """NewsCollector orchestration tests."""

    def test_collect_empty(self):
        """Collector returns empty list when no collectors are enabled."""
        collector = NewsCollector()
        # Clear all registered collectors
        collector._collectors = {}

        articles = collector.collect()
        assert articles == []

    def test_deduplicate(self):
        """Duplicate URLs are removed."""
        collector = NewsCollector()
        collector._collectors = {}

        article_a = Article(
            title="Duplicate Title",
            url="https://example.com/dup",
            source="rss",
            source_name="RSS A",
        )
        article_b = Article(
            title="Duplicate Title",
            url="https://example.com/dup",
            source="newsapi",
            source_name="NewsAPI B",
        )
        article_c = Article(
            title="Unique Article",
            url="https://example.com/unique",
            source="rss",
            source_name="RSS C",
        )

        with patch.object(collector, "_collectors", {
            "rss": MagicMock(fetch=MagicMock(return_value=[article_a])),
            "newsapi": MagicMock(fetch=MagicMock(return_value=[article_b, article_c])),
        }):
            articles = collector.collect()
            assert len(articles) == 2  # one duplicate removed
            assert articles[0].url == "https://example.com/dup"
            assert articles[1].url == "https://example.com/unique"

    def test_collector_failure_does_not_block_others(self):
        """One collector's failure should not stop others."""
        collector = NewsCollector()
        collector._collectors = {}

        with patch.object(collector, "_collectors", {
            "failing": MagicMock(fetch=MagicMock(side_effect=Exception("Boom!"))),
            "working": MagicMock(fetch=MagicMock(return_value=[
                Article(title="Good", url="https://example.com/good", source="test", source_name="Test"),
            ])),
        }):
            articles = collector.collect()
            assert len(articles) == 1
            assert articles[0].title == "Good"

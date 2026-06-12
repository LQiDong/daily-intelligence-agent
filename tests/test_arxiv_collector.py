"""Tests for ArXivCollector with mocked feedparser."""

from unittest.mock import patch, MagicMock

from src.collect.arxiv_collector import ArXivCollector


def _make_entry(**kwargs) -> dict:
    """Build a dict that mimics a feedparser entry (supports both .get() and attr access)."""
    return kwargs


class TestArXivCollector:
    """ArXivCollector unit tests."""

    @patch("src.collect.arxiv_collector.feedparser.parse")
    def test_fetch_success(self, mock_parse):
        """Collector returns papers from arXiv."""
        entry_1 = _make_entry(
            id="http://arxiv.org/abs/2401.00001",
            title="Attention Is All You Need\n",
            summary="A breakthrough paper about attention mechanisms.\n",
            published_parsed=(2026, 6, 10, 12, 0, 0, 2, 161, 0),
            arxiv_primary_category={"term": "cs.AI"},
            tags=[{"term": "cs.AI"}, {"term": "cs.LG"}],
            authors=[{"name": "Author A"}, {"name": "Author B"}],
        )
        entry_2 = _make_entry(
            id="http://arxiv.org/abs/2401.00002",
            title="Deep Learning Advances",
            summary="Advances in deep learning.\n",
            published_parsed=(2026, 6, 9, 8, 0, 0, 1, 160, 0),
            arxiv_primary_category={"term": "cs.LG"},
            tags=[{"term": "cs.LG"}],
            authors=[{"name": "Author C"}],
        )

        mock_parse.return_value = MagicMock(
            bozo=False,
            entries=[entry_1, entry_2],
        )

        collector = ArXivCollector()

        articles = collector._fetch_category("cs.AI")
        # mock returns all 2 entries; category filtering happens at API level, not in code
        assert len(articles) == 2
        assert articles[0].source == "arxiv"
        assert "Attention" in articles[0].title
        assert "Author A" in articles[0].author

    @patch("src.collect.arxiv_collector.feedparser.parse")
    def test_fetch_parse_error(self, mock_parse):
        """Parse error returns empty list."""
        mock_parse.return_value = MagicMock(
            bozo=True,
            bozo_exception=Exception("arXiv down"),
            entries=[],
        )

        collector = ArXivCollector()

        articles = collector.fetch()
        assert articles == []

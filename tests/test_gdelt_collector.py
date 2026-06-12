"""Tests for GDELTCollector with mocked requests."""

from unittest.mock import patch, MagicMock

from src.collect.gdelt_collector import GDELTCollector


class TestGDELTCollector:
    """GDELTCollector unit tests."""

    @patch("src.collect.gdelt_collector.requests.get")
    def test_fetch_success(self, mock_get, sample_gdelt_response):
        """Collector returns articles from GDELT."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = sample_gdelt_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        collector = GDELTCollector()

        articles = collector.fetch()
        # 3 queries x 2 results each = 6
        assert len(articles) == 6
        assert articles[0].title == "New quantum computing milestone achieved"
        assert articles[0].source == "gdelt"

    @patch("src.collect.gdelt_collector.requests.get")
    def test_fetch_empty_response(self, mock_get):
        """Empty response returns empty list."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        collector = GDELTCollector()

        articles = collector.fetch()
        assert articles == []

    @patch("src.collect.gdelt_collector.requests.get")
    def test_fetch_network_error(self, mock_get):
        """Network error is caught."""
        mock_get.side_effect = Exception("Network error")

        collector = GDELTCollector()

        articles = collector.fetch()
        assert articles == []

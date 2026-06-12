"""Tests for AlphaVantageCollector with mocked requests."""

from unittest.mock import patch, MagicMock

from src.collect.alpha_vantage_collector import AlphaVantageCollector


class TestAlphaVantageCollector:
    """AlphaVantageCollector unit tests."""

    @patch("src.collect.alpha_vantage_collector.requests.get")
    def test_fetch_success(self, mock_get, sample_alpha_vantage_response):
        """Collector returns articles from Alpha Vantage."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = sample_alpha_vantage_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        collector = AlphaVantageCollector()
        collector.api_key = "test-key"

        articles = collector.fetch()
        # 3 topics x 2 results each = 6
        assert len(articles) == 6
        assert articles[0].title == "Tech stocks rally on AI optimism"
        assert articles[0].source == "alpha_vantage"

    @patch("src.collect.alpha_vantage_collector.requests.get")
    def test_fetch_empty_api_key(self, mock_get):
        """Empty API key skips fetch."""
        collector = AlphaVantageCollector()
        collector.api_key = ""

        articles = collector.fetch()
        assert articles == []
        mock_get.assert_not_called()

    @patch("src.collect.alpha_vantage_collector.requests.get")
    def test_fetch_missing_feed(self, mock_get):
        """Response without 'feed' key returns empty list."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"Information": "Invalid API call"}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        collector = AlphaVantageCollector()
        collector.api_key = "test-key"

        articles = collector.fetch()
        assert articles == []

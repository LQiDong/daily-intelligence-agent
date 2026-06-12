"""Tests for NewsAPICollector with mocked requests."""

from unittest.mock import patch, MagicMock

from src.collect.newsapi_collector import NewsAPICollector


class TestNewsAPICollector:
    """NewsAPICollector unit tests."""

    @patch("src.collect.newsapi_collector.requests.get")
    def test_fetch_success(self, mock_get, sample_newsapi_response):
        """Collector returns articles from NewsAPI."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = sample_newsapi_response
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        collector = NewsAPICollector()
        collector.api_key = "test-key-123"

        articles = collector.fetch()
        # 3 queries x 2 results each = 6, deduped to 6 (all unique URLs)
        assert len(articles) == 6
        assert articles[0].title == "AI makes new breakthrough in healthcare"
        assert articles[0].source == "newsapi"
        assert articles[0].source_name == "Test News"

    @patch("src.collect.newsapi_collector.requests.get")
    def test_fetch_empty_api_key(self, mock_get):
        """Empty API key skips fetch."""
        collector = NewsAPICollector()
        collector.api_key = ""

        articles = collector.fetch()
        assert articles == []
        mock_get.assert_not_called()

    @patch("src.collect.newsapi_collector.requests.get")
    def test_fetch_api_error(self, mock_get):
        """API error returns empty list."""
        mock_get.side_effect = Exception("API error")

        collector = NewsAPICollector()
        collector.api_key = "test-key"

        articles = collector.fetch()
        assert articles == []

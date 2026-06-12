"""Pytest fixtures for all test modules."""

from datetime import datetime, timezone
from typing import Any

import pytest

from src.collect.models import Article


@pytest.fixture
def sample_article() -> Article:
    """Return a basic sample article."""
    return Article(
        title="Test AI Breakthrough",
        url="https://example.com/ai-breakthrough",
        source="rss",
        source_name="Test Source",
        published_at=datetime.now(timezone.utc),
        summary="A test article about AI.",
        categories=["AI", "Technology"],
        author="Test Author",
    )


@pytest.fixture
def sample_newsapi_response() -> dict[str, Any]:
    """Simulated NewsAPI /v2/everything response."""
    return {
        "status": "ok",
        "totalResults": 2,
        "articles": [
            {
                "source": {"id": "test-1", "name": "Test News"},
                "author": "Alice",
                "title": "AI makes new breakthrough in healthcare",
                "description": "A new AI model achieves state-of-the-art results.",
                "url": "https://example.com/ai-healthcare",
                "publishedAt": "2026-06-10T12:00:00Z",
                "content": "Full content here...",
            },
            {
                "source": {"id": "test-2", "name": "Tech Daily"},
                "author": "Bob",
                "title": "Stock market reaches new highs",
                "description": "Major indices hit record levels.",
                "url": "https://example.com/stock-market",
                "publishedAt": "2026-06-09T08:30:00Z",
                "content": "More content...",
            },
        ],
    }


@pytest.fixture
def sample_alpha_vantage_response() -> dict[str, Any]:
    """Simulated Alpha Vantage NEWS_SENTIMENT response."""
    return {
        "feed": [
            {
                "title": "Tech stocks rally on AI optimism",
                "url": "https://example.com/tech-rally",
                "time_published": "20260610T120000",
                "summary": "Technology stocks surged today.",
                "topics": [{"topic": "Technology"}, {"topic": "Finance"}],
                "authors": ["Charlie"],
            },
            {
                "title": "Blockchain startup raises $100M",
                "url": "https://example.com/blockchain-funding",
                "time_published": "20260609T080000",
                "summary": "A blockchain startup secured Series B funding.",
                "topics": [{"topic": "Blockchain"}, {"topic": "Finance"}],
                "authors": ["Diana"],
            },
        ]
    }


@pytest.fixture
def sample_gdelt_response() -> dict[str, Any]:
    """Simulated GDELT doc API response."""
    return {
        "articles": [
            {
                "title": "New quantum computing milestone achieved",
                "url": "https://example.com/quantum-milestone",
                "seendate": "20260610T140000",
                "summary": "Researchers achieve quantum supremacy milestone.",
                "domain": "science.example.com",
            },
            {
                "title": "Global markets react to interest rate decision",
                "url": "https://example.com/markets-rate",
                "seendate": "20260609T100000",
                "summary": "Stock markets worldwide respond to Fed decision.",
                "domain": "finance.example.com",
            },
        ]
    }

"""Integration tests for the full NewsProcessor pipeline."""

from datetime import datetime, timezone, timedelta

from src.collect.models import Article
from src.process.processor import NewsProcessor


def _article(
    title: str,
    url: str | None = None,
    category: str = "",
    published_at=None,
    summary: str = "",
    source_name: str = "TechCrunch",
) -> Article:
    return Article(
        title=title,
        url=url or f"https://example.com/{hash(title)}",
        source="rss",
        source_name=source_name,
        published_at=published_at or datetime.now(timezone.utc),
        summary=summary or f"Summary of {title}",
        category=category,
    )


class TestNewsProcessor:
    """NewsProcessor integration tests."""

    def test_empty_input(self):
        """Empty input returns empty result."""
        processor = NewsProcessor()
        result = processor.process([])
        assert result.all_articles == []
        assert result.top_global == []
        assert result.tech_top == []
        assert result.ai_top == []
        assert result.finance_top == []

    def test_full_pipeline(self):
        """Full pipeline processes articles end-to-end."""
        articles = [
            _article("OpenAI GPT-5 released with advanced reasoning",
                     summary="New large language model shows breakthrough in AI"),
            _article("Apple M4 chip announced for MacBook Pro",
                     summary="Apple's latest processor features improved performance"),
            _article("Fed holds interest rates steady amid inflation",
                     summary="Federal Reserve decides to maintain current rates"),
            _article("Startup raises $100M for AI-powered robotics",
                     summary="Venture capital funding round led by Sequoia"),
            _article("NVIDIA stock surges on AI chip demand",
                     summary="GPU maker reports record quarterly earnings"),
            _article("Weather forecast for the weekend",
                     summary="Sunny skies expected"),
        ]

        processor = NewsProcessor()
        result = processor.process(articles)

        # All articles processed
        assert len(result.all_articles) == 6

        # Categories assigned
        categories = {a.category for a in result.all_articles}
        assert "ai" in categories or "tech" in categories or "finance" in categories or "general" in categories

        # Scores assigned
        for art in result.all_articles:
            assert art.score > 0

        # Global top picks (up to 5)
        assert len(result.top_global) <= 5
        assert len(result.top_global) >= 1

        # Module top picks
        for group in [result.tech_top, result.ai_top, result.finance_top]:
            assert len(group) <= 8

    def test_pipeline_sort_order(self):
        """Top articles are sorted by score descending."""
        articles = [
            _article("Important: Apple announces major AI breakthrough with new chip",
                     summary="Apple and OpenAI partnership for AI development",
                     source_name="Reuters"),
            _article("Minor update to weather app",
                     summary="Small update released",
                     source_name="Unknown Blog"),
        ]
        processor = NewsProcessor()
        result = processor.process(articles)

        if len(result.top_global) >= 2:
            assert result.top_global[0].score >= result.top_global[1].score

    def test_to_flat_list(self):
        """ProcessResult.to_flat_list() returns all articles."""
        articles = [
            _article("Apple announces new AI chip", summary="Apple's latest chip features AI acceleration"),
            _article("Weather forecast for the weekend", summary="Sunny skies expected"),
        ]
        processor = NewsProcessor()
        result = processor.process(articles)
        flat = result.to_flat_list()
        assert len(flat) == 2

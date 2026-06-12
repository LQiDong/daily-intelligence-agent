"""Tests for the report context builder."""

from datetime import datetime, timezone, timedelta

from src.collect.models import Article
from src.generate.report_context import (
    build_report_context,
    _article_to_dict,
    _relative_time,
)
from src.process.processor import ProcessResult


def _article(
    title: str,
    category: str = "tech",
    score: float = 70.0,
    hours_ago: float = 5,
    source_name: str = "Test",
    analysis: dict | None = None,
) -> Article:
    published_at = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    a = Article(
        title=title,
        url=f"https://example.com/{hash(title)}",
        source="rss",
        source_name=source_name,
        published_at=published_at,
        summary=f"Summary of {title}",
        categories=[category],
        author="Author",
        category=category,
        score=score,
        analysis=analysis,
    )
    if score >= 80:
        a.is_global_top = True
        a.is_module_top = True
    elif score >= 60:
        a.is_module_top = True
    return a


class TestReportContext:
    """Report context builder unit tests."""

    def test_build_context_minimal(self):
        """Build context with empty result."""
        result = ProcessResult(
            all_articles=[], top_global=[], tech_top=[], finance_top=[], ai_top=[], general_top=[]
        )
        ctx = build_report_context(result)
        assert ctx["date"] is not None
        assert ctx["total_articles"] == 0
        assert ctx["top_global"] == []
        assert ctx["ai"] == []

    def test_build_context_with_articles(self):
        """Build context with articles."""
        articles = [
            _article("AI News", category="ai", score=90.0),
            _article("Tech News", category="tech", score=80.0),
            _article("Finance News", category="finance", score=75.0),
        ]
        result = ProcessResult(
            all_articles=articles,
            top_global=[articles[0], articles[1]],
            tech_top=[articles[1]],
            ai_top=[articles[0]],
            finance_top=[articles[2]],
            general_top=[],
        )
        ctx = build_report_context(result)
        assert ctx["total_articles"] == 3
        assert len(ctx["top_global"]) == 2
        assert len(ctx["ai"]) == 1
        assert len(ctx["tech"]) == 1
        assert len(ctx["finance"]) == 1
        assert ctx["ai"][0]["title"] == "AI News"

    def test_article_to_dict_conversion(self):
        """Article to dict includes all expected display fields."""
        art = _article("Test Title", category="tech", score=85.0)
        d = _article_to_dict(art)
        assert d["title"] == "Test Title"
        assert d["score_display"] == "85.0"
        assert d["published_at_cn"] is not None
        assert d["published_at_relative"] is not None
        assert d["analysis_insufficient"] is True
        assert d["analysis_one_sentence"] == ""

    def test_article_to_dict_with_analysis(self):
        """Article with LLM analysis includes analysis fields."""
        analysis = {
            "one_sentence_conclusion": "This is a test conclusion",
            "why_important": "Important reason",
            "potential_impact": ["Impact 1"],
            "follow_up_points": ["Watch point"],
            "insufficient_info": False,
        }
        art = _article("Analysis Article", analysis=analysis)
        d = _article_to_dict(art)
        assert d["analysis_one_sentence"] == "This is a test conclusion"
        assert d["analysis_why_important"] == "Important reason"
        assert d["analysis_impact"] == ["Impact 1"]
        assert d["analysis_follow_up"] == ["Watch point"]
        assert d["analysis_insufficient"] is False

    def test_relative_time(self):
        """Relative time returns correct Chinese string."""
        now = datetime.now(timezone.utc)
        assert "分钟前" in _relative_time(now - timedelta(minutes=30))
        assert "小时前" in _relative_time(now - timedelta(hours=3))
        assert "天前" in _relative_time(now - timedelta(days=2))

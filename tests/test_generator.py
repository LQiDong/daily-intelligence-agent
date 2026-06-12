"""Tests for the ReportGenerator integration."""

from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.collect.models import Article
from src.generate.generator import ReportGenerator
from src.process.processor import ProcessResult


def _article(title: str, category: str = "tech", score: float = 70.0) -> Article:
    return Article(
        title=title,
        url=f"https://example.com/{hash(title)}",
        source="rss",
        source_name="Test",
        published_at=datetime.now(timezone.utc) - timedelta(hours=3),
        summary=f"Summary of {title}",
        categories=[category],
        author="Author",
        category=category,
        score=score,
    )


class TestReportGenerator:
    """ReportGenerator integration tests."""

    def test_generate_with_empty_result(self, tmp_path):
        """Generate with empty result creates files."""
        result = ProcessResult(
            all_articles=[],
            top_global=[],
            tech_top=[],
            finance_top=[],
            ai_top=[],
            general_top=[],
        )
        generator = ReportGenerator(output_dir=str(tmp_path))
        html = generator.generate(result)
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html

        # Check files exist
        date_str = datetime.now().strftime("%Y_%m_%d")
        md_path = tmp_path / f"report_{date_str}.md"
        html_path = tmp_path / f"report_{date_str}.html"
        assert md_path.exists()
        assert html_path.exists()

    def test_generate_with_articles(self, tmp_path):
        """Generate with articles creates rich report."""
        articles = [
            _article("AI Breakthrough", category="ai", score=92.0),
            _article("Tech Innovation", category="tech", score=85.0),
            _article("Finance Update", category="finance", score=78.0),
        ]
        result = ProcessResult(
            all_articles=articles,
            top_global=articles[:2],
            tech_top=[articles[1]],
            ai_top=[articles[0]],
            finance_top=[articles[2]],
            general_top=[],
        )
        generator = ReportGenerator(output_dir=str(tmp_path))
        html = generator.generate(result)

        assert "AI Breakthrough" in html
        assert "Tech Innovation" in html
        assert "Finance Update" in html

        # Check markdown file content
        date_str = datetime.now().strftime("%Y_%m_%d")
        md_path = tmp_path / f"report_{date_str}.md"
        md_content = md_path.read_text(encoding="utf-8")
        assert "AI Breakthrough" in md_content
        assert "Tech Innovation" in md_content

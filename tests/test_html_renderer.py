"""Tests for the HTML report renderer."""

from src.generate.html_renderer import render_html


class TestHTMLRenderer:
    """HTML renderer unit tests."""

    def test_render_empty_context(self):
        """Render with minimal context should not crash."""
        ctx = {
            "date": "2026-06-11",
            "date_cn": "2026年6月11日",
            "total_articles": 0,
            "top_global": [],
            "ai": [],
            "tech": [],
            "finance": [],
            "general": [],
            "trend_summary": "",
            "trends": [],
            "follow_up": {"ai": [], "tech": [], "finance": []},
        }
        html = render_html(ctx)
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "每日情报简报" in html
        assert "2026年6月11日" in html
        assert html.strip() != ""

    def test_render_with_articles(self):
        """Render with articles generates proper sections."""
        ctx = {
            "date": "2026-06-11",
            "date_cn": "2026年6月11日",
            "total_articles": 3,
            "top_global": [
                {
                    "title": "Test Headline",
                    "url": "https://example.com/headline",
                    "source_name": "Reuters",
                    "score_display": "92.5",
                    "published_at_cn": "2026-06-11 09:00",
                    "published_at_relative": "3小时前",
                    "analysis_insufficient": True,
                    "analysis_one_sentence": "",
                    "analysis_why_important": "",
                    "analysis_impact": [],
                    "analysis_follow_up": [],
                    "summary": "This is a test.",
                    "categories": [],
                    "author": "",
                    "category": "",
                    "score": 92.5,
                }
            ],
            "ai": [],
            "tech": [],
            "finance": [],
            "general": [],
            "trend_summary": "趋势总结",
            "trends": ["趋势1"],
            "follow_up": {"ai": ["观察点A"], "tech": [], "finance": []},
        }
        html = render_html(ctx)
        assert "section-top_global" in html
        assert "Test Headline" in html
        assert "92.5" in html
        assert "section-trends" in html
        assert "趋势1" in html
        assert "section-followup" in html
        assert "观察点A" in html

    def test_html_structure(self):
        """HTML has proper structure (responsive, mobile-friendly)."""
        ctx = {
            "date": "2026-06-11",
            "date_cn": "2026年6月11日",
            "total_articles": 0,
            "top_global": [],
            "ai": [],
            "tech": [],
            "finance": [],
            "general": [],
            "trend_summary": "",
            "trends": [],
            "follow_up": {"ai": [], "tech": [], "finance": []},
        }
        html = render_html(ctx)
        # Viewport meta for mobile
        assert 'name="viewport"' in html
        # Has CSS
        assert "<style>" in html
        # Container
        assert 'class="container"' in html
        # Badge classes
        assert "badge-score" in html or "toc" in html

    def test_html_with_analysis(self):
        """HTML renders LLM analysis content."""
        ctx = {
            "date": "2026-06-11",
            "date_cn": "2026年6月11日",
            "total_articles": 1,
            "top_global": [
                {
                    "title": "AI Breakthrough",
                    "url": "https://example.com/ai",
                    "source_name": "TechCrunch",
                    "score_display": "88.0",
                    "published_at_cn": "2026-06-11 06:00",
                    "published_at_relative": "6小时前",
                    "analysis_insufficient": False,
                    "analysis_one_sentence": "AI achieves new milestone",
                    "analysis_why_important": "Important for the industry",
                    "analysis_impact": ["Impact A"],
                    "analysis_follow_up": [],
                    "summary": "",
                    "categories": [],
                    "author": "",
                    "category": "ai",
                    "score": 88.0,
                }
            ],
            "ai": [],
            "tech": [],
            "finance": [],
            "general": [],
            "trend_summary": "",
            "trends": [],
            "follow_up": {"ai": [], "tech": [], "finance": []},
        }
        html = render_html(ctx)
        assert "AI achieves new milestone" in html
        assert "Important for the industry" in html
        assert "Impact A" in html

"""Tests for the Markdown report renderer."""

from src.generate.markdown_renderer import render_markdown


class TestMarkdownRenderer:
    """Markdown renderer unit tests."""

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
        md = render_markdown(ctx)
        assert isinstance(md, str)
        assert "每日情报简报" in md
        assert "2026-06-11" in md
        assert md.strip() != ""

    def test_render_with_articles(self):
        """Render with articles generates proper sections."""
        ctx = {
            "date": "2026-06-11",
            "date_cn": "2026年6月11日",
            "total_articles": 5,
            "top_global": [
                {
                    "title": "Test Article",
                    "url": "https://example.com/test",
                    "source_name": "Test Source",
                    "score_display": "85.0",
                    "published_at_cn": "2026-06-11 10:00",
                    "published_at_relative": "2小时前",
                    "analysis_insufficient": True,
                    "analysis_one_sentence": "",
                    "analysis_why_important": "",
                    "analysis_impact": [],
                    "analysis_follow_up": [],
                    "summary": "This is a test summary.",
                    "categories": ["AI"],
                    "author": "",
                    "category": "ai",
                    "score": 85.0,
                }
            ],
            "ai": [],
            "tech": [],
            "finance": [],
            "general": [],
            "trend_summary": "今日共采集并处理 5 篇新闻。",
            "trends": ["AI 领域持续发展"],
            "follow_up": {"ai": ["关注GPT-5发布"], "tech": [], "finance": []},
        }
        md = render_markdown(ctx)
        assert "今日最重要" in md
        assert "Test Article" in md
        assert "85.0" in md
        assert "今日趋势判断" in md
        assert "AI 领域持续发展" in md
        assert "明日继续跟踪" in md
        assert "关注GPT-5发布" in md
        assert "https://example.com/test" in md

    def test_render_with_llm_analysis(self):
        """Render shows LLM analysis when available."""
        ctx = {
            "date": "2026-06-11",
            "date_cn": "2026年6月11日",
            "total_articles": 1,
            "top_global": [
                {
                    "title": "AI News",
                    "url": "https://example.com/ai",
                    "source_name": "TechCrunch",
                    "score_display": "90.0",
                    "published_at_cn": "2026-06-11 08:00",
                    "published_at_relative": "5小时前",
                    "analysis_insufficient": False,
                    "analysis_one_sentence": "这是一篇关于AI突破的报道",
                    "analysis_why_important": "将改变行业发展方向",
                    "analysis_impact": ["加速AI落地", "引发竞争"],
                    "analysis_follow_up": ["关注后续进展"],
                    "summary": "AI summary.",
                    "categories": ["AI"],
                    "author": "",
                    "category": "ai",
                    "score": 90.0,
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
        md = render_markdown(ctx)
        assert "一句话结论" in md
        assert "这是一篇关于AI突破的报道" in md
        assert "将改变行业发展方向" in md
        assert "加速AI落地" in md
        assert "引发竞争" in md

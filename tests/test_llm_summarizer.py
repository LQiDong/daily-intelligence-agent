"""Tests for ArticleSummarizer with mock mode.

All tests use MOCK_LLM=true to avoid real API calls.
"""

import os

import pytest

from src.generate.llm.summarizer import ArticleSummarizer


@pytest.fixture(autouse=True)
def enable_mock():
    """Enable mock mode for all tests in this module."""
    old = os.environ.get("MOCK_LLM")
    os.environ["MOCK_LLM"] = "true"
    yield
    if old is None:
        del os.environ["MOCK_LLM"]
    else:
        os.environ["MOCK_LLM"] = old


class TestArticleSummarizerMock:
    """ArticleSummarizer tests with mocked LLM responses."""

    def test_analyze_normal_article(self):
        """Normal article returns structured analysis."""
        summarizer = ArticleSummarizer()
        analysis = summarizer.analyze(
            title="Apple releases new M4 chip for MacBook Pro",
            summary="Apple announced the new M4 processor with improved performance and efficiency.",
            source_name="TechCrunch",
        )
        assert not analysis.insufficient_info
        assert "Apple releases new M4 chip" in analysis.one_sentence_conclusion
        assert len(analysis.key_facts) >= 1
        assert analysis.why_important
        assert len(analysis.potential_impact) >= 1
        assert len(analysis.follow_up_points) >= 1

    def test_analyze_empty_article(self):
        """Empty article returns insufficient_info=True."""
        summarizer = ArticleSummarizer()
        analysis = summarizer.analyze(
            title="",
            summary="",
            source_name="Test",
        )
        assert analysis.insufficient_info is True
        assert analysis.insufficient_reason == "原文标题或正文为空"

    def test_analyze_empty_summary(self):
        """Article with title but empty summary returns insufficient_info."""
        summarizer = ArticleSummarizer()
        analysis = summarizer.analyze(
            title="Some Title",
            summary="",
            source_name="Test",
        )
        assert analysis.insufficient_info is True

    def test_analyze_batch(self):
        """Batch analysis processes multiple articles."""
        summarizer = ArticleSummarizer()
        articles = [
            {"title": "News A", "summary": "Content A.", "source_name": "Src A"},
            {"title": "News B", "summary": "Content B.", "source_name": "Src B"},
            {"title": "", "summary": "", "source_name": "Src C"},
        ]
        results = summarizer.analyze_batch(articles)
        assert len(results) == 3
        assert not results[0].insufficient_info
        assert not results[1].insufficient_info
        assert results[2].insufficient_info is True

    def test_parse_response_normal(self):
        """Parse a normal JSON response from LLM."""
        raw = """{
            "one_sentence_conclusion": "This is a test conclusion",
            "key_facts": ["Fact 1", "Fact 2"],
            "why_important": "It matters because of X",
            "potential_impact": ["Impact 1"],
            "follow_up_points": ["Watch for Y"],
            "insufficient_info": false,
            "insufficient_reason": ""
        }"""
        analysis = ArticleSummarizer._parse_response(raw, "Test Title")
        assert analysis.one_sentence_conclusion == "This is a test conclusion"
        assert analysis.key_facts == ["Fact 1", "Fact 2"]
        assert analysis.why_important == "It matters because of X"
        assert not analysis.insufficient_info

    def test_parse_response_with_markdown_fence(self):
        """Parse JSON wrapped in markdown code fences."""
        raw = """```json
{
    "one_sentence_conclusion": "Test conclusion",
    "key_facts": ["Fact 1"],
    "why_important": "",
    "potential_impact": [],
    "follow_up_points": [],
    "insufficient_info": false,
    "insufficient_reason": ""
}
```"""
        analysis = ArticleSummarizer._parse_response(raw, "Test")
        assert analysis.one_sentence_conclusion == "Test conclusion"
        assert analysis.key_facts == ["Fact 1"]

    def test_parse_response_invalid_json(self):
        """Invalid JSON returns fallback."""
        raw = "This is not JSON at all"
        analysis = ArticleSummarizer._parse_response(raw, "Test")
        assert analysis.insufficient_info is True
        assert "JSON" in analysis.insufficient_reason

    def test_parse_response_partial_fields(self):
        """Response with missing fields still works."""
        raw = '{"one_sentence_conclusion": "Only this field"}'
        analysis = ArticleSummarizer._parse_response(raw, "Test")
        assert analysis.one_sentence_conclusion == "Only this field"
        assert analysis.key_facts == []
        assert analysis.why_important == ""

    def test_analyze_exception_handling(self):
        """When mock mode is off and no API key, analysis returns error fallback."""
        # Temporarily disable mock for this test
        os.environ["MOCK_LLM"] = "false"
        # Remove the API key
        import src.config.settings as settings_mod
        from src.config import get_settings

        # Clear the cached settings
        get_settings.cache_clear()
        settings = get_settings()
        old_key = settings.openai_api_key
        settings.openai_api_key = ""

        summarizer = ArticleSummarizer()
        analysis = summarizer.analyze(
            title="Test",
            summary="Test content",
            source_name="Test",
        )
        # Should get error fallback
        assert analysis.insufficient_info is True

        # Restore
        settings.openai_api_key = old_key
        get_settings.cache_clear()
        os.environ["MOCK_LLM"] = "true"

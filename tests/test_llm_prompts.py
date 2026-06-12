"""Tests for LLM prompt templates."""

from src.generate.llm.prompts import (
    SUMMARY_SYSTEM_PROMPT,
    build_summary_user_prompt,
)


class TestPrompts:
    """Prompt template tests."""

    def test_system_prompt_contains_key_rules(self):
        """System prompt contains anti-hallucination rules."""
        assert "严禁编造" in SUMMARY_SYSTEM_PROMPT
        assert "信息不足" in SUMMARY_SYSTEM_PROMPT
        assert "JSON" in SUMMARY_SYSTEM_PROMPT

    def test_system_prompt_contains_output_fields(self):
        """System prompt mentions all required output fields."""
        assert "one_sentence_conclusion" in SUMMARY_SYSTEM_PROMPT
        assert "key_facts" in SUMMARY_SYSTEM_PROMPT
        assert "why_important" in SUMMARY_SYSTEM_PROMPT
        assert "potential_impact" in SUMMARY_SYSTEM_PROMPT
        assert "follow_up_points" in SUMMARY_SYSTEM_PROMPT
        assert "insufficient_info" in SUMMARY_SYSTEM_PROMPT

    def test_build_user_prompt_contains_article(self):
        """User prompt includes the article title and summary."""
        prompt = build_summary_user_prompt(
            title="GPT-5 Released",
            summary="OpenAI released GPT-5 with improved reasoning.",
            source_name="TechCrunch",
        )
        assert "GPT-5 Released" in prompt
        assert "OpenAI released GPT-5" in prompt
        assert "TechCrunch" in prompt

    def test_build_user_prompt_empty_title(self):
        """User prompt handles empty title gracefully."""
        prompt = build_summary_user_prompt(
            title="",
            summary="Some article content.",
            source_name="Test",
        )
        assert "标题：" in prompt
        assert "Some article content." in prompt

"""Tests for ArticleAnalysis model."""

from src.generate.llm.models import ArticleAnalysis


class TestArticleAnalysis:
    """ArticleAnalysis model unit tests."""

    def test_default_values(self):
        """Default ArticleAnalysis has empty fields."""
        analysis = ArticleAnalysis()
        assert analysis.one_sentence_conclusion == ""
        assert analysis.key_facts == []
        assert analysis.why_important == ""
        assert analysis.potential_impact == []
        assert analysis.follow_up_points == []
        assert analysis.insufficient_info is False
        assert analysis.insufficient_reason == ""

    def test_full_analysis(self):
        """Create a complete analysis with all fields."""
        analysis = ArticleAnalysis(
            one_sentence_conclusion="OpenAI 发布了 GPT-5",
            key_facts=["OpenAI 在 6 月 10 日发布了 GPT-5", "新模型在推理能力上有显著提升"],
            why_important="这是 AI 领域最重要的模型发布之一",
            potential_impact=["加速 AI 应用落地", "引发新一轮 AI 竞争"],
            follow_up_points=["关注 GPT-5 在实际场景中的表现", "观察竞争对手的反应"],
            insufficient_info=False,
            insufficient_reason="",
        )
        assert analysis.one_sentence_conclusion == "OpenAI 发布了 GPT-5"
        assert len(analysis.key_facts) == 2
        assert len(analysis.potential_impact) == 2
        assert analysis.insufficient_info is False

    def test_insufficient_info(self):
        """insufficient_info flag works correctly."""
        analysis = ArticleAnalysis(
            insufficient_info=True,
            insufficient_reason="原文信息不足，无法判断新闻主题",
        )
        assert analysis.insufficient_info is True
        assert "信息不足" in analysis.insufficient_reason

    def test_to_dict_roundtrip(self):
        """ArticleAnalysis can be serialized to dict and loaded back."""
        analysis = ArticleAnalysis(
            one_sentence_conclusion="Test conclusion",
            key_facts=["Fact 1", "Fact 2"],
        )
        d = analysis.model_dump()
        assert d["one_sentence_conclusion"] == "Test conclusion"
        assert len(d["key_facts"]) == 2

        loaded = ArticleAnalysis(**d)
        assert loaded.one_sentence_conclusion == "Test conclusion"
        assert loaded.key_facts == ["Fact 1", "Fact 2"]

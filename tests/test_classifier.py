"""Tests for the Classifier module."""

from src.collect.models import Article
from src.process.classifier import Classifier, classify_single


class TestClassifier:
    """Classifier unit tests."""

    def test_classify_ai(self):
        """AI-related article is classified as ai."""
        art = Article(
            title="New GPT Model Shows Breakthrough in Reasoning",
            url="https://example.com/gpt",
            source="rss", source_name="Test",
            summary="OpenAI's latest large language model demonstrates advanced reasoning.",
        )
        assert classify_single(art) == "ai"

    def test_classify_tech(self):
        """Tech-related article is classified as tech."""
        art = Article(
            title="Apple Announces New M4 Chip for MacBook Pro",
            url="https://example.com/apple",
            source="rss", source_name="Test",
            summary="The new processor features improved performance and efficiency.",
        )
        assert classify_single(art) == "tech"

    def test_classify_finance(self):
        """Finance-related article is classified as finance."""
        art = Article(
            title="Federal Reserve Holds Interest Rates Steady",
            url="https://example.com/fed",
            source="rss", source_name="Test",
            summary="The central bank decided to keep rates unchanged amid inflation concerns.",
        )
        assert classify_single(art) == "finance"

    def test_classify_general(self):
        """Article with no matching keywords is classified as general."""
        art = Article(
            title="Local Community Hosts Charity Event",
            url="https://example.com/charity",
            source="rss", source_name="Test",
            summary="Volunteers gather for annual fundraising picnic in the park.",
        )
        assert classify_single(art) == "general"

    def test_classify_ai_with_tech_terms(self):
        """AI-specific article is classified as ai even when tech keywords appear."""
        art = Article(
            title="DeepMind's New RL Algorithm Outperforms Previous Benchmarks",
            url="https://example.com/deepmind-rl",
            source="rss", source_name="Test",
            summary="A novel reinforcement learning approach achieves state-of-the-art results.",
        )
        assert classify_single(art) == "ai"

    def test_classifier_batch(self):
        """Classifier handles batch classification."""
        articles = [
            Article(title="AI Model Advances", url="https://example.com/1", source="rss", source_name="Test",
                    summary="New deep learning techniques."),
            Article(title="Stock Market Rally", url="https://example.com/2", source="rss", source_name="Test",
                    summary="Markets reach new highs."),
            Article(title="New Chip Announcement", url="https://example.com/3", source="rss", source_name="Test",
                    summary="Intel releases new processor."),
        ]
        classifier = Classifier()
        result = classifier.classify(articles)
        assert result[0].category == "ai"
        assert result[1].category == "finance"
        assert result[2].category == "tech"

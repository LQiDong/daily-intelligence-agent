"""Tests for the Scorer module."""

from datetime import datetime, timezone, timedelta

from src.collect.models import Article
from src.process.scorer import Scorer


def _make_article(
    title: str,
    category: str = "tech",
    source_name: str = "TechCrunch",
    author: str = "Test Author",
    hours_ago: float | None = 6,
    summary: str = "",
    source: str = "rss",
) -> Article:
    published_at = None
    if hours_ago is not None:
        published_at = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return Article(
        title=title,
        url=f"https://example.com/{hash(title)}",
        source=source,
        source_name=source_name,
        author=author,
        published_at=published_at,
        summary=summary or f"A summary about {title.lower()}.",
        category=category,
    )


class TestScorer:
    """Scorer unit tests."""

    def test_score_influence_major_company(self):
        """Mentioning a major company increases influence score."""
        art = _make_article("Apple and Google announce partnership")
        scorer = Scorer()
        score = scorer._score_influence(art)
        assert score >= 30  # base 20 + 2 companies = +20

    def test_score_influence_no_company(self):
        """No major company mentioned gets base score."""
        art = _make_article("Weather forecast for the weekend", author="")
        score = Scorer._score_influence(art)
        assert score == 20.0

    def test_score_influence_signal_words(self):
        """Signal words in title increase score."""
        art = _make_article("Breakthrough: Major milestone achieved in quantum computing")
        score = Scorer._score_influence(art)
        assert score > 20

    def test_score_credibility_known_source(self):
        """Known source returns correct credibility score."""
        art = _make_article("Test", source_name="Reuters")
        assert Scorer._score_credibility(art) == 92

    def test_score_credibility_unknown_source(self):
        """Unknown source returns default score."""
        art = _make_article("Test", source_name="Unknown Blog")
        assert Scorer._score_credibility(art) == 55

    def test_score_timeliness_very_recent(self):
        """Very recent article gets high score."""
        art = _make_article("Recent News", hours_ago=2)
        assert Scorer._score_timeliness(art) == 100

    def test_score_timeliness_old(self):
        """Old article gets low score."""
        art = _make_article("Old News", hours_ago=100)
        assert Scorer._score_timeliness(art) == 30

    def test_score_timeliness_no_date(self):
        """Article without date gets neutral score."""
        art = _make_article("No Date", hours_ago=None)
        assert Scorer._score_timeliness(art) == 50

    def test_score_relevance_ai(self):
        """AI article with AI keywords gets high relevance."""
        art = _make_article(
            "GPT-4 and machine learning breakthroughs",
            category="ai",
            summary="Large language models using deep learning and neural networks.",
        )
        score = Scorer._score_relevance(art)
        assert score >= 60

    def test_score_relevance_general(self):
        """General article gets moderate relevance."""
        art = _make_article("Weather Report", category="general")
        assert Scorer._score_relevance(art) == 30

    def test_score_novelty_unique(self):
        """Unique article gets high novelty."""
        art_a = _make_article("AI Breakthrough in Healthcare", category="ai")
        art_b = _make_article("Stock Market Rally Continues", category="finance")
        score = Scorer._score_novelty(art_a, [art_a, art_b])
        assert score > 50

    def test_total_score_range(self):
        """Total score is between 0 and 100."""
        articles = [
            _make_article("Apple releases new iPhone with AI features", category="tech"),
            _make_article("Fed raises interest rates", category="finance"),
        ]
        scorer = Scorer()
        scored = scorer.score(articles)
        for art in scored:
            assert 0 <= art.score <= 100

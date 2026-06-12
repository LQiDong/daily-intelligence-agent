"""Scorer — scores articles on 5 dimensions (influence, relevance, credibility, timeliness, novelty)."""

from datetime import datetime, timezone, timedelta

from loguru import logger

from src.collect.models import Article


# Source credibility map (0-100)
_CREDIBILITY_MAP: dict[str, float] = {
    "Reuters": 92, "Bloomberg": 92, "The New York Times": 90,
    "The Wall Street Journal": 90, "The Washington Post": 88,
    "Financial Times": 90, "BBC News": 85, "CNN": 78,
    "The Guardian": 82, "Wired": 80, "TechCrunch": 75,
    "The Verge": 75, "Ars Technica": 80, "MIT Technology Review": 88,
    "Nature": 95, "Science": 95, "arXiv": 70,
    "Hacker News": 60, "Reddit": 40, "Medium": 45,
    "Forbes": 70, "Business Insider": 68, "CNBC": 75,
    "Bloomberg Technology": 88, "Bloomberg Markets": 85,
    "GDELT": 60, "NewsAPI": 50, "Alpha Vantage": 65,
}

# Default credibility for unknown sources
_DEFAULT_CREDIBILITY = 55

# Major tech companies (influence signal)
_MAJOR_COMPANIES: set[str] = {
    "apple", "google", "alphabet", "microsoft", "amazon", "meta",
    "facebook", "nvidia", "tesla", "openai", "spacex", "intel",
    "amd", "ibm", "oracle", "salesforce", "netflix", "adobe",
    "twitter", "x", "snap", "uber", "airbnb", "stripe",
    "palantir", "crowdstrike", "datadog", "cloudflare",
    "tencent", "alibaba", "baidu", "bytedance", "huawei",
    "samsung", "sony", "tsmc", "qualcomm", "broadcom",
    "jpmorgan", "goldman sachs", "morgan stanley", "blackrock",
    "berkshire", "vanguard", "fidelity", "coinbase",
}


class Scorer:
    """Score articles on 5 dimensions and compute a composite total score."""

    # Weight for each dimension in the total score
    WEIGHTS = {
        "influence": 0.30,
        "relevance": 0.25,
        "credibility": 0.15,
        "timeliness": 0.20,
        "novelty": 0.10,
    }

    def score(self, articles: list[Article]) -> list[Article]:
        """Score all articles in-place and return them."""
        if not articles:
            return []

        for article in articles:
            article.influence_score = self._score_influence(article)
            article.relevance_score = self._score_relevance(article)
            article.credibility_score = self._score_credibility(article)
            article.timeliness_score = self._score_timeliness(article)
            article.novelty_score = self._score_novelty(article, articles)

            article.score = (
                self.WEIGHTS["influence"] * article.influence_score
                + self.WEIGHTS["relevance"] * article.relevance_score
                + self.WEIGHTS["credibility"] * article.credibility_score
                + self.WEIGHTS["timeliness"] * article.timeliness_score
                + self.WEIGHTS["novelty"] * article.novelty_score
            )

        logger.info(
            f"Scorer: scored {len(articles)} articles, "
            f"score range {min(a.score for a in articles):.1f}-{max(a.score for a in articles):.1f}"
        )
        return articles

    @staticmethod
    def _keyword_in_text(keyword: str, text: str) -> bool:
        """Check if keyword appears as a whole word in text."""
        import re

        if " " in keyword:
            return keyword in text
        return bool(re.search(rf"\b{re.escape(keyword)}\b", text))

    @staticmethod
    def _score_influence(article: Article) -> float:
        """Score 0-100 based on mention of major companies and author prominence."""
        score = 20.0  # base score
        text = f"{article.title} {article.summary}".lower()

        # Major companies mentioned → +10 each, max +50
        found_companies = [c for c in _MAJOR_COMPANIES if Scorer._keyword_in_text(c, text)]
        score += min(len(found_companies) * 10, 50)

        # Author present → +10
        if article.author.strip():
            score += 10

        # Title contains strong signal words → +5 each, max +20
        signal_words = ["breakthrough", "revolutionary", "landmark", "milestone",
                        "unprecedented", "historic", "major", "significant",
                        "critical", "urgent", "crisis", "record"]
        for word in signal_words:
            if Scorer._keyword_in_text(word, article.title.lower()):
                score += 5
        score = min(score, 100)

        return score

    @staticmethod
    def _score_relevance(article: Article) -> float:
        """Score 0-100 based on keyword density matched to the assigned category."""
        from .classifier import _AI_KEYWORDS, _TECH_KEYWORDS, _FINANCE_KEYWORDS, _PM_KEYWORDS, _keyword_in_text

        text = f"{article.title} {article.summary}".lower()

        category_keywords = {
            "ai": _AI_KEYWORDS,
            "tech": _TECH_KEYWORDS,
            "finance": _FINANCE_KEYWORDS,
            "pm": _PM_KEYWORDS,
        }

        keywords = category_keywords.get(article.category, set())
        if not keywords:
            return 30.0  # general articles get a moderate relevance

        hits = sum(1 for kw in keywords if _keyword_in_text(kw, text))
        # Scale: 0 hits → 20, 1-2 → 40, 3-4 → 60, 5-7 → 80, 8+ → 100
        if hits == 0:
            return 20.0
        if hits <= 2:
            return 40.0
        if hits <= 4:
            return 60.0
        if hits <= 7:
            return 80.0
        return 100.0

    @staticmethod
    def _score_credibility(article: Article) -> float:
        """Score 0-100 based on source credibility map."""
        # Check exact match first, then partial match
        source = article.source_name.strip()
        if source in _CREDIBILITY_MAP:
            return _CREDIBILITY_MAP[source]

        # Partial match: "TechCrunch" in "TechCrunch News" etc.
        for known_name, cred in _CREDIBILITY_MAP.items():
            if known_name.lower() in source.lower() or source.lower() in known_name.lower():
                return cred

        # Check by source identifier
        source_id_cred = {
            "arxiv": 70, "newsapi": 50, "rss": 55,
            "gdelt": 60, "alpha_vantage": 65,
        }
        return source_id_cred.get(article.source, _DEFAULT_CREDIBILITY)

    @staticmethod
    def _score_timeliness(article: Article) -> float:
        """Score 0-100 based on recency. Recent = higher."""
        if article.published_at is None:
            return 50.0  # neutral for unknown dates

        now = datetime.now(timezone.utc)
        hours_ago = (now - article.published_at).total_seconds() / 3600

        if hours_ago <= 6:
            return 100.0
        if hours_ago <= 12:
            return 90.0
        if hours_ago <= 24:
            return 80.0
        if hours_ago <= 48:
            return 65.0
        if hours_ago <= 72:
            return 50.0
        return 30.0

    @staticmethod
    def _score_novelty(article: Article, all_articles: list[Article]) -> float:
        """Score 0-100. Novelty decreases when many other articles share the same topic.

        Uses word overlap with all other articles as a proxy for novelty.
        Less overlap = more novel.
        """
        import re

        def tokenize(text: str) -> set[str]:
            words = re.findall(r"[a-zA-Z]{4,}", text.lower())
            return set(words)

        article_tokens = tokenize(f"{article.title} {article.summary}")
        if not article_tokens:
            return 50.0

        total_overlap = 0.0
        count = 0
        for other in all_articles:
            if other.url == article.url and other.title == article.title:
                continue
            other_tokens = tokenize(f"{other.title} {other.summary}")
            if not other_tokens:
                continue
            overlap = len(article_tokens & other_tokens) / len(article_tokens | other_tokens)
            total_overlap += overlap
            count += 1

        if count == 0:
            return 80.0  # only article → reasonably novel

        avg_overlap = total_overlap / count
        # High overlap = low novelty
        novelty = max(0, 100 - (avg_overlap * 100))
        return novelty

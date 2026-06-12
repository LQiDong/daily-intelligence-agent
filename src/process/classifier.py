"""Classifier — assigns each article to a module category (tech / finance / ai / general)."""

from loguru import logger

from src.collect.models import Article


# Keyword sets for each module domain
_AI_KEYWORDS: set[str] = {
    "artificial intelligence", "machine learning", "deep learning", "neural network",
    "llm", "large language model", "gpt", "openai", "chatgpt", "claude", "gemini",
    "transformer", "attention mechanism", "reinforcement learning", "nlp",
    "natural language processing", "computer vision", "image recognition",
    "generative ai", "diffusion model", "stable diffusion", "dall-e",
    "ai agent", "autonomous", "rag", "retrieval augmented",
    "fine-tuning", "pretrained", "foundation model", "multimodal",
    "ai safety", "alignment", "hallucination", "prompt engineering",
    "langchain", "pytorch", "tensorflow", "hugging face",
    "mlops", "ai ethics", "explainable ai", "xai",
    "gpu training", "inference", "token", "embedding",
    "vector database", "semantic search", "chatbot", "copilot",
}

_TECH_KEYWORDS: set[str] = {
    "technology", "startup", "software", "hardware", "cloud", "cloud computing",
    "aws", "azure", "google cloud", "saas", "paas", "iaas", "devops",
    "cybersecurity", "security", "hack", "ransomware", "data breach",
    "quantum", "quantum computing", "blockchain", "web3", "crypto",
    "semiconductor", "chip", "processor", "intel", "nvidia", "amd", "arm",
    "5g", "6g", "network", "internet", "iot", "robotics",
    "virtual reality", "augmented reality", "metaverse", "vr", "ar",
    "open source", "github", "gitlab", "api", "microservice",
    "kubernetes", "docker", "container", "edge computing",
    "database", "sql", "nosql", "big data", "data science",
    "electric vehicle", "ev", "autonomous vehicle", "self-driving",
    "spacex", "nasa", "space", "rocket", "satellite",
    "apple", "google", "microsoft", "meta", "amazon", "tesla",
    "iphone", "android", "ios", "macos", "windows", "linux",
    "app store", "developer", "programming", "coding", "algorithm",
}

_FINANCE_KEYWORDS: set[str] = {
    "stock", "stock market", "finance", "financial", "economy", "economic",
    "recession", "inflation", "interest rate", "fed", "federal reserve",
    "central bank", "monetary policy", "fiscal policy", "gdp", "growth",
    "bond", "treasury", "yield", "equity", "etf", "mutual fund",
    "ipo", "venture capital", "vc", "private equity", "pe",
    "merger", "acquisition", "m&a", "spin-off", "divestiture",
    "earnings", "revenue", "profit", "quarterly report",
    "bank", "banking", "investment", "investor", "funding",
    "series a", "series b", "series c", "seed round", "valuation",
    "cryptocurrency", "bitcoin", "ethereum", "defi", "nft",
    "fintech", "payments", "digital payment", "blockchain finance",
    "s&p 500", "nasdaq", "dow jones", "index", "bull market",
    "bear market", "volatility", "trade", "tariff", "sanction",
    "hedge fund", "sovereign wealth", "asset management",
    "dividend", "buyback", "shareholder", "corporate finance",
    "wealth", "fortune", "billion", "million funding",
    "wall street", "silicon valley bank", "svb", "credit",
    "debt", "loan", "mortgage", "real estate", "housing market",
}


def _normalize_text(text: str) -> str:
    """Lowercase and normalize whitespace."""
    import re

    return re.sub(r"\s+", " ", text.lower()).strip()


def _keyword_in_text(keyword: str, text: str) -> bool:
    """Check if a keyword appears in text with word boundaries for single words."""
    import re

    if " " in keyword:
        # Multi-word keyword: use substring (already precise)
        return keyword in text
    # Single-word keyword: require word boundary
    pattern = rf"\b{re.escape(keyword)}\b"
    return bool(re.search(pattern, text))


def classify_single(article: Article) -> str:
    """Determine the primary category for a single article.

    Returns one of: 'ai', 'tech', 'finance', 'general'.
    """
    text = _normalize_text(f"{article.title} {article.summary} ")

    # Count keyword matches for each domain
    ai_hits = sum(1 for kw in _AI_KEYWORDS if _keyword_in_text(kw, text))
    tech_hits = sum(1 for kw in _TECH_KEYWORDS if _keyword_in_text(kw, text))
    finance_hits = sum(1 for kw in _FINANCE_KEYWORDS if _keyword_in_text(kw, text))

    # Weighted scoring with second-pass for cross-domain articles
    # AI gets bonus because it's a higher-priority signal
    scores = {
        "ai": ai_hits * 1.2,
        "tech": tech_hits * 1.0,
        "finance": finance_hits * 1.0,
    }

    best = max(scores, key=scores.get)
    if scores[best] <= 0:
        return "general"

    return best


class Classifier:
    """Assign each article to a module category."""

    def classify(self, articles: list[Article]) -> list[Article]:
        """Classify all articles and return them with `.category` set."""
        if not articles:
            return []

        for article in articles:
            article.category = classify_single(article)

        # Log distribution
        counts = {}
        for a in articles:
            counts[a.category] = counts.get(a.category, 0) + 1
        dist = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        logger.info(f"Classifier: {len(articles)} articles → {dist}")

        return articles

"""Deduplication — remove duplicate articles by URL and title similarity."""

from difflib import SequenceMatcher

from loguru import logger

from src.collect.models import Article


class Deduper:
    """Remove duplicate articles based on URL identity and title similarity."""

    TITLE_SIMILARITY_THRESHOLD = 0.75

    def deduplicate(self, articles: list[Article]) -> list[Article]:
        """Deduplicate by URL first, then by title similarity."""
        if not articles:
            return []

        # Phase 1: dedup by URL (exact match)
        url_seen: dict[str, Article] = {}
        for a in articles:
            key = a.url.strip().rstrip("/")
            if key not in url_seen:
                url_seen[key] = a
            else:
                logger.debug(f"Deduper: URL duplicate removed '{a.title[:50]}'")

        articles = list(url_seen.values())

        # Phase 2: dedup by title similarity (fuzzy)
        kept: list[Article] = []
        for a in articles:
            if not self._is_duplicate_title(a, kept):
                kept.append(a)
            else:
                logger.debug(f"Deduper: title-similar duplicate removed '{a.title[:50]}'")

        logger.info(f"Deduper: {len(articles)} (after URL) → {len(kept)} (after title)")
        return kept

    @classmethod
    def _is_duplicate_title(cls, candidate: Article, existing: list[Article]) -> bool:
        """Check if candidate title is too similar to any existing article's title."""
        candidate_tokens = cls._normalize(candidate.title)
        if not candidate_tokens:
            return False

        for art in existing:
            existing_tokens = cls._normalize(art.title)
            if not existing_tokens:
                continue
            similarity = cls._jaccard_similarity(candidate_tokens, existing_tokens)
            # Also check sequence matcher for short titles
            seq_ratio = SequenceMatcher(
                None, candidate.title.lower(), art.title.lower()
            ).ratio()
            if similarity >= cls.TITLE_SIMILARITY_THRESHOLD or seq_ratio >= 0.8:
                return True
        return False

    @staticmethod
    def _normalize(text: str) -> set[str]:
        """Tokenize and normalize title text into a set of meaningful words."""
        import re

        words = re.findall(r"[a-zA-Z0-9]+", text.lower())
        # Filter out very short or common stop words
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "has", "have", "had", "do", "does", "did", "will", "would",
            "can", "could", "may", "might", "shall", "should", "to", "of",
            "in", "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "this", "that", "these", "those", "it", "its", "and", "or",
            "but", "not", "no", "nor", "so", "if", "then", "than",
        }
        return {w for w in words if len(w) > 2 and w not in stop_words}

    @staticmethod
    def _jaccard_similarity(a: set[str], b: set[str]) -> float:
        """Compute Jaccard similarity between two sets of tokens."""
        if not a or not b:
            return 0.0
        intersection = a & b
        union = a | b
        return len(intersection) / len(union)

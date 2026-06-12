"""Data cleaning — remove malformed or invalid articles."""

from datetime import datetime, timezone, timedelta

from loguru import logger

from src.collect.models import Article


class Cleaner:
    """Filter out articles with empty titles, invalid URLs, or abnormal timestamps."""

    def clean(self, articles: list[Article]) -> list[Article]:
        """Run all cleaning rules and return the surviving articles."""
        if not articles:
            return []

        cleaned = articles
        cleaned = self._remove_empty_title(cleaned)
        cleaned = self._remove_invalid_url(cleaned)
        cleaned = self._trim_strings(cleaned)
        cleaned = self._remove_abnormal_time(cleaned)

        logger.info(f"Cleaner: {len(articles)} → {len(cleaned)} articles")
        return cleaned

    @staticmethod
    def _remove_empty_title(articles: list[Article]) -> list[Article]:
        """Remove articles with empty or whitespace-only titles."""
        kept = [a for a in articles if a.title and a.title.strip()]
        dropped = len(articles) - len(kept)
        if dropped:
            logger.debug(f"Cleaner: removed {dropped} articles with empty title")
        return kept

    @staticmethod
    def _remove_invalid_url(articles: list[Article]) -> list[Article]:
        """Remove articles with missing or invalid URLs."""
        kept = []
        for a in articles:
            url = (a.url or "").strip()
            if url and url.startswith(("http://", "https://")):
                kept.append(a)
        dropped = len(articles) - len(kept)
        if dropped:
            logger.debug(f"Cleaner: removed {dropped} articles with invalid URL")
        return kept

    @staticmethod
    def _remove_abnormal_time(articles: list[Article]) -> list[Article]:
        """Remove articles with future dates or dates older than 7 days."""
        now = datetime.now(timezone.utc)
        kept = []
        for a in articles:
            if a.published_at is None:
                kept.append(a)  # keep articles without dates
                continue
            if a.published_at > now + timedelta(hours=1):
                logger.debug(f"Cleaner: removed future-dated article '{a.title[:40]}'")
                continue
            if now - a.published_at > timedelta(days=7):
                logger.debug(f"Cleaner: removed too-old article '{a.title[:40]}'")
                continue
            kept.append(a)
        dropped = len(articles) - len(kept)
        if dropped:
            logger.debug(f"Cleaner: removed {dropped} articles with abnormal time")
        return kept

    @staticmethod
    def _trim_strings(articles: list[Article]) -> list[Article]:
        """Trim whitespace from all string fields."""
        trimmed = []
        for a in articles:
            trimmed.append(
                Article(
                    title=a.title.strip(),
                    url=a.url.strip(),
                    source=a.source.strip(),
                    source_name=a.source_name.strip(),
                    published_at=a.published_at,
                    summary=a.summary.strip(),
                    categories=[c.strip() for c in a.categories if c.strip()],
                    author=a.author.strip(),
                )
            )
        return trimmed

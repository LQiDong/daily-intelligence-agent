"""RSS feed collector using feedparser."""

from datetime import datetime, timezone

import feedparser
from loguru import logger

from src.collect.base import BaseCollector
from src.collect.models import Article
from src.config import get_settings


class RSSCollector(BaseCollector):
    """Fetch articles from configurable RSS/Atom feeds."""

    def __init__(self) -> None:
        super().__init__()
        settings = get_settings()
        self.feeds = settings.rss_feeds
        self.timeout = settings.http_timeout

    def fetch(self) -> list[Article]:
        """Parse all configured RSS feeds and return recent articles."""
        all_articles: list[Article] = []
        for feed_url in self.feeds:
            try:
                articles = self._fetch_single(feed_url)
                all_articles.extend(articles)
                logger.info(f"RSS [{feed_url}]: got {len(articles)} articles")
            except Exception as exc:
                logger.error(f"RSS fetch failed [{feed_url}]: {exc}")
        return self.filter_recent(all_articles)

    def _fetch_single(self, feed_url: str) -> list[Article]:
        """Fetch and parse a single RSS/Atom feed."""
        parsed = feedparser.parse(feed_url)
        if parsed.bozo and not parsed.entries:
            raise ValueError(f"Feed parse error: {parsed.bozo_exception}")

        articles: list[Article] = []
        feed_title = parsed.feed.get("title", feed_url)

        for entry in parsed.entries:
            url = entry.get("link", "")
            if not url:
                continue

            pub_time = self._extract_time(entry)
            categories = [t.get("term", "") for t in entry.get("tags", []) if t.get("term")]
            categories = [c for c in categories if c]

            article = Article(
                title=entry.get("title", "").strip(),
                url=url,
                source="rss",
                source_name=feed_title,
                published_at=pub_time,
                summary=self._clean_summary(entry.get("summary", "")),
                categories=categories,
                author=entry.get("author", ""),
            )
            articles.append(article)

        return articles

    def _extract_time(self, entry: dict) -> datetime | None:
        """Extract published time from a feed entry, return UTC datetime."""
        pub_tuple = entry.get("published_parsed") or entry.get("updated_parsed")
        if pub_tuple:
            import calendar
            import time

            try:
                ts = time.mktime(pub_tuple)
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            except (TypeError, OSError, OverflowError):
                try:
                    # fallback: treat as UTC and use calendar.timegm
                    ts = calendar.timegm(pub_tuple)
                    return datetime.fromtimestamp(ts, tz=timezone.utc)
                except (TypeError, OSError, OverflowError):
                    return None
        return None

    @staticmethod
    def _clean_summary(raw: str) -> str:
        """Strip HTML tags from summary text."""
        if not raw:
            return ""
        import re

        clean = re.sub(r"<[^>]+>", "", raw)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean[:500]

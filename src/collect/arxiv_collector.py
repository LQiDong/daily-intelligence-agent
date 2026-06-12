"""arXiv API collector for recent AI/ML/CS papers."""

from datetime import datetime, timezone, timedelta

import feedparser
from loguru import logger

from src.collect.base import BaseCollector
from src.collect.models import Article


class ArXivCollector(BaseCollector):
    """Fetch recent papers from arXiv API sorted by announcement date."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self) -> None:
        super().__init__()
        self.max_results = 50

    def fetch(self) -> list[Article]:
        """Query arXiv for recent AI, ML, and CS papers."""
        categories = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "q-fin"]
        all_articles: list[Article] = []
        for cat in categories:
            try:
                articles = self._fetch_category(cat)
                all_articles.extend(articles)
                logger.info(f"arXiv [{cat}]: got {len(articles)} papers")
            except Exception as exc:
                logger.error(f"arXiv category [{cat}] failed: {exc}")

        return self.filter_recent(all_articles)

    def _fetch_category(self, category: str) -> list[Article]:
        """Fetch recent papers for a single arXiv category."""
        query_params = f"cat:{category}+AND+submittedDate:[{self._date_3days_ago()}TO{self._date_today()}]"
        url = (
            f"{self.BASE_URL}?search_query={query_params}"
            f"&sortBy=submittedDate&sortOrder=descending"
            f"&max_results={self.max_results}"
        )

        parsed = feedparser.parse(url)
        if parsed.bozo and not parsed.entries:
            raise ValueError(f"arXiv parse error: {parsed.bozo_exception}")

        articles: list[Article] = []
        for entry in parsed.entries:
            url = entry.get("id", "")
            if not url:
                continue

            pub_time = self._extract_time(entry)

            # arXiv categories from <arxiv:primary_category> and <category> tags
            categories = []
            primary_cat = entry.get("arxiv_primary_category")
            if primary_cat:
                categories.append(primary_cat.get("term", "") if isinstance(primary_cat, dict) else primary_cat)
            for cat_tag in entry.get("tags", []):
                term = cat_tag.get("term", "") if isinstance(cat_tag, dict) else getattr(cat_tag, "term", "")
                if term and term not in categories:
                    categories.append(term)

            article = Article(
                title=(entry.get("title", "").replace("\n", " ").strip()),
                url=url,
                source="arxiv",
                source_name="arXiv",
                published_at=pub_time,
                summary=(entry.get("summary", "").replace("\n", " ").strip()[:500]),
                categories=categories,
                author=", ".join(
                    [a.get("name", "") for a in entry.get("authors", []) if a.get("name")]
                ),
            )
            articles.append(article)

        return articles

    def _extract_time(self, entry: dict) -> datetime | None:
        """Extract published time from arXiv entry."""
        pub_tuple = entry.get("published_parsed")
        if pub_tuple:
            import calendar
            import time

            try:
                ts = time.mktime(pub_tuple)
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            except (TypeError, OSError, OverflowError):
                try:
                    ts = calendar.timegm(pub_tuple)
                    return datetime.fromtimestamp(ts, tz=timezone.utc)
                except (TypeError, OSError, OverflowError):
                    return None
        return None

    @staticmethod
    def _date_3days_ago() -> str:
        """Return date string 3 days ago in YYYYMMDD format."""
        d = datetime.now(timezone.utc) - timedelta(days=3)
        return d.strftime("%Y%m%d")

    @staticmethod
    def _date_today() -> str:
        """Return today's date string in YYYYMMDD format."""
        return datetime.now(timezone.utc).strftime("%Y%m%d")

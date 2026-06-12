"""GDELT Project collector using the GKG (Global Knowledge Graph) API."""

from datetime import datetime, timezone, timedelta
from urllib.parse import quote

import requests
from loguru import logger

from src.collect.base import BaseCollector
from src.collect.models import Article
from src.config import get_settings


class GDELTCollector(BaseCollector):
    """Fetch articles from GDELT's free GKG API."""

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self) -> None:
        super().__init__()
        settings = get_settings()
        self.timeout = settings.http_timeout
        self.max_records = settings.gdelt_max_records

    def fetch(self) -> list[Article]:
        """Query GDELT for recent tech/finance/AI articles."""
        now = datetime.now(timezone.utc)
        three_days_ago = now - timedelta(days=3)
        start_date = three_days_ago.strftime("%Y%m%dT%H%M%S")

        queries = [
            "artificial intelligence machine learning",
            "stock market finance economy",
            "technology startup cybersecurity",
        ]

        all_articles: list[Article] = []
        for query in queries:
            try:
                articles = self._fetch_query(query, start_date)
                all_articles.extend(articles)
                logger.info(f"GDELT [{query[:40]}...]: got {len(articles)} articles")
            except Exception as exc:
                logger.error(f"GDELT query failed [{query[:40]}...]: {exc}")

        return self.filter_recent(all_articles)

    def _fetch_query(self, query: str, start_date: str) -> list[Article]:
        """Execute a single GDELT doc query."""
        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": str(self.max_records),
            "startdatetime": start_date,
            "sort": "DateDesc",
        }
        resp = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        articles: list[Article] = []
        for item in data.get("articles", []):
            pub_time = None
            if item.get("seendate"):
                try:
                    pub_time = datetime.strptime(item["seendate"], "%Y%m%dT%H%M%S").replace(
                        tzinfo=timezone.utc
                    )
                except (ValueError, TypeError):
                    pass

            article = Article(
                title=(item.get("title") or "").strip(),
                url=(item.get("url") or "").strip(),
                source="gdelt",
                source_name="GDELT",
                published_at=pub_time,
                summary=(item.get("summary") or "").strip()[:500],
                categories=[item.get("domain", "")] if item.get("domain") else [],
                author="",
            )
            if article.title and article.url:
                articles.append(article)

        return articles

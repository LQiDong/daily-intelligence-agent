"""Alpha Vantage news sentiment collector."""

from datetime import datetime, timezone

import requests
from loguru import logger

from src.collect.base import BaseCollector
from src.collect.models import Article
from src.config import get_settings


class AlphaVantageCollector(BaseCollector):
    """Fetch financial news from Alpha Vantage NEWS_SENTIMENT endpoint."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self) -> None:
        super().__init__()
        settings = get_settings()
        self.api_key = settings.alpha_vantage_api_key
        self.timeout = settings.http_timeout

    def fetch(self) -> list[Article]:
        """Query Alpha Vantage for recent financial news."""
        if not self.api_key:
            logger.warning("AlphaVantageCollector: ALPHA_VANTAGE_API_KEY not set, skipping")
            return []

        topics = ["technology", "finance", "blockchain"]
        all_articles: list[Article] = []
        for topic in topics:
            try:
                articles = self._fetch_topic(topic)
                all_articles.extend(articles)
                logger.info(f"AlphaVantage [{topic}]: got {len(articles)} articles")
            except Exception as exc:
                logger.error(f"AlphaVantage topic [{topic}] failed: {exc}")

        return self.filter_recent(all_articles)

    def _fetch_topic(self, topic: str) -> list[Article]:
        """Fetch news for a single topic."""
        params = {
            "function": "NEWS_SENTIMENT",
            "topics": topic,
            "apikey": self.api_key,
            "limit": 50,
        }
        resp = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if "feed" not in data:
            logger.warning(f"AlphaVantage: no 'feed' in response for topic '{topic}'")
            return []

        articles: list[Article] = []
        for item in data["feed"]:
            pub_time = None
            if item.get("time_published"):
                try:
                    pub_time = datetime.strptime(
                        item["time_published"], "%Y%m%dT%H%M%S"
                    ).replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    pass

            categories = [t.get("topic", "") for t in item.get("topics", []) if t.get("topic")]

            article = Article(
                title=(item.get("title") or "").strip(),
                url=(item.get("url") or "").strip(),
                source="alpha_vantage",
                source_name="Alpha Vantage",
                published_at=pub_time,
                summary=(item.get("summary") or "").strip()[:500],
                categories=categories,
                author=(item.get("authors") or [""])[0] if item.get("authors") else "",
            )
            if article.title and article.url:
                articles.append(article)

        return articles

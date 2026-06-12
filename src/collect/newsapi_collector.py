"""NewsAPI.org collector."""

from datetime import datetime, timezone, timedelta

import requests
from loguru import logger

from src.collect.base import BaseCollector
from src.collect.models import Article
from src.config import get_settings


class NewsAPICollector(BaseCollector):
    """Fetch articles from NewsAPI.org /v2/everything endpoint."""

    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self) -> None:
        super().__init__()
        settings = get_settings()
        self.api_key = settings.newsapi_api_key
        self.timeout = settings.http_timeout
        self.page_size = settings.newsapi_page_size

    def fetch(self) -> list[Article]:
        """Query NewsAPI for tech, finance, and AI news from last 3 days."""
        if not self.api_key:
            logger.warning("NewsAPICollector: NEWSAPI_API_KEY not set, skipping")
            return []

        from_date = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%d")
        queries = [
            '"artificial intelligence" OR "machine learning" OR "deep learning" OR "LLM" OR "GPT"',
            '"stock market" OR finance OR "venture capital" OR IPO OR blockchain',
            "technology OR startup OR cybersecurity OR cloud OR quantum",
        ]

        all_articles: list[Article] = []
        for query in queries:
            try:
                articles = self._fetch_query(query, from_date)
                all_articles.extend(articles)
                logger.info(f"NewsAPI [{query[:40]}...]: got {len(articles)} articles")
            except Exception as exc:
                logger.error(f"NewsAPI query failed [{query[:40]}...]: {exc}")

        return self.filter_recent(all_articles)

    def _fetch_query(self, query: str, from_date: str) -> list[Article]:
        """Execute a single NewsAPI query."""
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "publishedAt",
            "pageSize": self.page_size,
            "apiKey": self.api_key,
            "language": "en",
        }
        resp = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "ok":
            raise ValueError(f"NewsAPI error: {data.get('message', 'unknown')}")

        articles: list[Article] = []
        for item in data.get("articles", []):
            pub_time = None
            if item.get("publishedAt"):
                pub_time = datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00"))

            article = Article(
                title=item.get("title", "").strip(),
                url=item.get("url", ""),
                source="newsapi",
                source_name=item.get("source", {}).get("name", "NewsAPI"),
                published_at=pub_time,
                summary=(item.get("description") or "").strip(),
                categories=[],
                author=item.get("author", ""),
            )
            if article.title and article.url:
                articles.append(article)

        return articles

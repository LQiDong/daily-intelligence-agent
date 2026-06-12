"""NewsCollector — orchestrates all configured collectors."""

from loguru import logger

from src.collect.alpha_vantage_collector import AlphaVantageCollector
from src.collect.arxiv_collector import ArXivCollector
from src.collect.base import BaseCollector
from src.collect.gdelt_collector import GDELTCollector
from src.collect.models import Article
from src.collect.newsapi_collector import NewsAPICollector
from src.collect.rss_collector import RSSCollector
from src.config import get_settings


class NewsCollector:
    """Orchestrate all news collectors and merge results."""

    def __init__(self) -> None:
        settings = get_settings()

        self._collectors: dict[str, BaseCollector] = {}

        if settings.collector_rss_enabled:
            self._collectors["rss"] = RSSCollector()
        if settings.collector_newsapi_enabled:
            self._collectors["newsapi"] = NewsAPICollector()
        if settings.collector_gdelt_enabled:
            self._collectors["gdelt"] = GDELTCollector()
        if settings.collector_alpha_vantage_enabled:
            self._collectors["alpha_vantage"] = AlphaVantageCollector()
        if settings.collector_arxiv_enabled:
            self._collectors["arxiv"] = ArXivCollector()

        logger.info(
            f"NewsCollector initialized with {len(self._collectors)} collectors: "
            f"{', '.join(self._collectors.keys())}"
        )

    def collect(self) -> list[Article]:
        """Fetch articles from all enabled collectors and merge results."""
        logger.info("Starting news collection...")
        all_articles: list[Article] = []

        for name, collector in self._collectors.items():
            try:
                articles = collector.fetch()
                all_articles.extend(articles)
                logger.info(f"[{name}] collected {len(articles)} articles")
            except Exception as exc:
                logger.error(f"[{name}] collector failed: {exc}")

        # Deduplicate by URL
        seen_urls: set[str] = set()
        deduped: list[Article] = []
        for art in all_articles:
            if art.url not in seen_urls:
                seen_urls.add(art.url)
                deduped.append(art)

        logger.info(
            f"Collection complete: {len(all_articles)} raw → "
            f"{len(deduped)} unique articles"
        )
        return deduped

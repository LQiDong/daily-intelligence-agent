"""Abstract base class for all news collectors."""

from abc import ABC, abstractmethod

from loguru import logger

from src.collect.models import Article


class BaseCollector(ABC):
    """All collectors must inherit from this class."""

    def __init__(self) -> None:
        self._name = self.__class__.__name__
        logger.debug(f"{self._name} initialized")

    @abstractmethod
    def fetch(self) -> list[Article]:
        """Fetch articles from the source. Must be implemented by subclasses."""
        ...

    def filter_recent(self, articles: list[Article], days: int = 3) -> list[Article]:
        """Keep only articles published within the last `days` days."""
        kept = [a for a in articles if a.is_recent(days)]
        dropped = len(articles) - len(kept)
        if dropped:
            logger.info(f"{self._name}: filtered out {dropped} outdated articles")
        return kept

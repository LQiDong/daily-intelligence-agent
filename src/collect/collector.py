"""News collection module — placeholder."""

from loguru import logger


class NewsCollector:
    """Collect news from multiple sources."""

    def __init__(self) -> None:
        logger.info("NewsCollector initialized")

    def collect(self) -> list[dict]:
        """Fetch raw news from all configured sources."""
        logger.info("Starting news collection...")
        # TODO: implement RSS / API fetching
        return []

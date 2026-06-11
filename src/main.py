"""Daily Intelligence Agent — entry point."""

from loguru import logger

from src.collect import NewsCollector
from src.config import get_settings
from src.generate import ReportGenerator
from src.process import NewsProcessor
from src.send import EmailSender
from src.utils import setup_logger


def main() -> None:
    """Run the daily intelligence pipeline."""
    setup_logger()

    settings = get_settings()
    logger.info("Daily Intelligence Agent starting...")
    logger.info("Configuration loaded:")
    logger.info("  Log level: {}", settings.log_level)
    logger.info("  Fetch days: {}", settings.fetch_days)
    logger.info("  Scheduled time: {}", settings.scheduled_time)

    collector = NewsCollector()
    processor = NewsProcessor()
    generator = ReportGenerator()
    sender = EmailSender()

    raw_news = collector.collect()
    articles = processor.process(raw_news)
    report = generator.generate(articles)
    if report:
        sender.send(report)

    logger.info("Daily Intelligence Agent finished.")


if __name__ == "__main__":
    main()

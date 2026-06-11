"""Logging utilities using loguru."""

import sys
from pathlib import Path

from loguru import logger

from src.config import get_settings


def setup_logger() -> None:
    """Configure loguru with file and console sinks."""
    settings = get_settings()
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(exist_ok=True)

    logger.remove()

    # Console sink
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    )

    # File sink (daily rotation)
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention=f"{settings.data_retention_days} days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        encoding="utf-8",
    )

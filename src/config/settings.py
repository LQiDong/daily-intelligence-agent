"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with type validation."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM API
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"

    # Anthropic API
    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_model: str = "claude-sonnet-4-20250514"

    # LLM provider selection ("openai" or "anthropic")
    llm_provider: str = "openai"

    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""
    email_to: str = ""
    smtp_retry_count: int = 3
    smtp_retry_delay: int = 5
    smtp_use_ssl: bool = False

    # App
    log_level: str = "INFO"
    data_retention_days: int = 7
    fetch_days: int = 3
    scheduled_time: str = "08:00"

    # HTTP
    http_timeout: int = 30

    # ---- Collector API Keys ----
    newsapi_api_key: str = ""
    alpha_vantage_api_key: str = ""

    # ---- Collector switches ----
    collector_rss_enabled: bool = True
    collector_newsapi_enabled: bool = True
    collector_gdelt_enabled: bool = True
    collector_alpha_vantage_enabled: bool = True
    collector_arxiv_enabled: bool = True

    # ---- Collector-specific config ----
    rss_feeds: list[str] = [
        "https://hnrss.org/frontpage",
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
    ]
    newsapi_page_size: int = 20
    gdelt_max_records: int = 50

    # ---- Processing configuration ----
    top_per_module: int = 8
    top_global: int = 5


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()

"""Pydantic data models for news articles."""

from datetime import datetime

from pydantic import BaseModel, Field


class Article(BaseModel):
    """Unified article data structure.

    Collectors produce Articles with only the core fields.
    The processing pipeline enriches them with category, score, and ranking fields.
    """

    # --- Core fields (filled by collectors) ---
    title: str = Field(..., description="Article title")
    url: str = Field(..., description="Article URL")
    source: str = Field(..., description="Collector source identifier, e.g. rss, newsapi")
    source_name: str = Field(..., description="Human-readable source name")
    published_at: datetime | None = Field(None, description="Publication time (UTC)")
    summary: str = Field("", description="Article summary or description")
    categories: list[str] = Field(default_factory=list, description="Topic categories")
    author: str = Field("", description="Author name if available")

    # --- Processing enrichment fields (filled by processor pipeline) ---
    category: str = Field("", description="Assigned module category: tech / finance / ai / general")
    score: float = Field(0.0, description="Total composite score 0-100")
    influence_score: float = Field(0.0, description="Influence dimension 0-100")
    relevance_score: float = Field(0.0, description="Relevance dimension 0-100")
    credibility_score: float = Field(0.0, description="Source credibility dimension 0-100")
    timeliness_score: float = Field(0.0, description="Timeliness dimension 0-100")
    novelty_score: float = Field(0.0, description="Novelty dimension 0-100")
    is_module_top: bool = Field(False, description="Top article in its category")
    is_global_top: bool = Field(False, description="Global top 5 article")

    # --- LLM analysis (filled by generate/llm) ---
    analysis: dict | None = Field(None, description="LLM analysis result dict (ArticleAnalysis)")

    def is_recent(self, days: int = 3) -> bool:
        """Check if article was published within the last `days` days."""
        if self.published_at is None:
            return True  # keep articles without dates
        from datetime import timezone

        delta = datetime.now(timezone.utc) - self.published_at
        return delta.days < days

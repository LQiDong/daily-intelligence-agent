"""NewsProcessor — orchestrates the full processing pipeline.

Pipeline order:
  cleaner → deduper → classifier → scorer → top-picker
"""

from loguru import logger

from src.collect.models import Article
from src.config import get_settings
from src.process.cleaner import Cleaner
from src.process.classifier import Classifier
from src.process.deduper import Deduper
from src.process.scorer import Scorer


class ProcessResult:
    """Container for processing results."""

    def __init__(
        self,
        all_articles: list[Article],
        top_global: list[Article],
        tech_top: list[Article],
        finance_top: list[Article],
        ai_top: list[Article],
        general_top: list[Article],
    ) -> None:
        self.all_articles = all_articles
        self.top_global = top_global
        self.tech_top = tech_top
        self.finance_top = finance_top
        self.ai_top = ai_top
        self.general_top = general_top

    @property
    def module_groups(self) -> dict[str, list[Article]]:
        return {
            "ai": self.ai_top,
            "tech": self.tech_top,
            "finance": self.finance_top,
        }

    def to_flat_list(self) -> list[Article]:
        """Return all articles as a flat list (used by downstream modules)."""
        return self.all_articles


class NewsProcessor:
    """Orchestrate cleaning, dedup, classification, scoring, and top-picking."""

    def __init__(self) -> None:
        self.cleaner = Cleaner()
        self.deduper = Deduper()
        self.classifier = Classifier()
        self.scorer = Scorer()
        self.settings = get_settings()
        logger.info("NewsProcessor initialized")

    def process(self, raw_news: list[Article]) -> ProcessResult:
        """Run the full processing pipeline on raw articles.

        Args:
            raw_news: Articles from the collector stage.

        Returns:
            ProcessResult with all articles, global top, and per-module top picks.
        """
        logger.info(f"Processing {len(raw_news)} articles...")

        # Step 1: Clean
        articles = self.cleaner.clean(raw_news)
        logger.info(f"  After clean: {len(articles)}")

        # Step 2: Deduplicate
        articles = self.deduper.deduplicate(articles)
        logger.info(f"  After dedup: {len(articles)}")

        # Step 3: Classify
        articles = self.classifier.classify(articles)
        logger.info(f"  After classify: {len(articles)}")

        # Step 4: Score
        articles = self.scorer.score(articles)
        logger.info(f"  After score: {len(articles)}")

        # Step 5: Pick top articles
        result = self._pick_top(articles)

        logger.info(
            f"Pipeline complete: tech={len(result.tech_top)}, "
            f"finance={len(result.finance_top)}, "
            f"ai={len(result.ai_top)}, "
            f"global_top={len(result.top_global)}"
        )
        return result

    def _pick_top(self, articles: list[Article]) -> ProcessResult:
        """Pick top articles per category and globally."""
        top_per_module = self.settings.top_per_module  # 8
        top_global = self.settings.top_global  # 5

        # Sort once by score descending
        sorted_all = sorted(articles, key=lambda a: a.score, reverse=True)

        # Global top N
        global_top = sorted_all[:top_global]
        for art in global_top:
            art.is_global_top = True

        # Per-module top N
        categories = {"ai": [], "tech": [], "finance": [], "general": []}
        for a in articles:
            cat = a.category if a.category in categories else "general"
            categories[cat].append(a)

        for cat in categories:
            categories[cat].sort(key=lambda a: a.score, reverse=True)
            for art in categories[cat][:top_per_module]:
                art.is_module_top = True

        return ProcessResult(
            all_articles=articles,
            top_global=global_top,
            tech_top=categories["tech"][:top_per_module],
            finance_top=categories["finance"][:top_per_module],
            ai_top=categories["ai"][:top_per_module],
            general_top=categories["general"][:top_per_module],
        )

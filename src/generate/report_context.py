"""Build the rendering context from ProcessResult for report templates."""

from datetime import datetime, timezone

from loguru import logger

from src.collect.models import Article
from src.process.processor import ProcessResult


def build_report_context(result: ProcessResult) -> dict:
    """Build a serializable dict context from a ProcessResult for rendering.

    Args:
        result: Output of NewsProcessor.process()

    Returns:
        A dict with the following structure:
        {
            "date": "2026-06-11",
            "date_cn": "2026年6月11日",
            "total_articles": int,
            "top_global": [...]   (Article dicts, up to 5)
            "ai": [...]           (top AI articles, up to 8)
            "tech": [...]         (top tech articles)
            "finance": [...]      (top finance articles)
            "general": [...]      (top general articles)
            "trend_summary": "str",
            "trends": ["str", ...],
            "follow_up": {"ai": [...], "tech": [...], "finance": [...]},
        }
        Each article dict contains all Article fields + a "published_at_cn" string.
    """
    now = datetime.now(timezone.utc)

    ctx: dict = {
        "date": now.strftime("%Y-%m-%d"),
        "date_cn": f"{now.year}年{now.month}月{now.day}日",
        "total_articles": len(result.all_articles),
        "top_global": [_article_to_dict(a) for a in result.top_global],
        "ai": [_article_to_dict(a) for a in result.ai_top],
        "tech": [_article_to_dict(a) for a in result.tech_top],
        "finance": [_article_to_dict(a) for a in result.finance_top],
        "pm": [_article_to_dict(a) for a in result.pm_top],
        "general": [_article_to_dict(a) for a in result.general_top],
    }

    # Aggregate trends and follow-up points from LLM analysis
    ctx["trend_summary"] = _build_trend_summary(ctx, now)
    ctx["trends"] = _build_trends(ctx)
    ctx["follow_up"] = {
        "ai": _collect_follow_ups(result.ai_top),
        "tech": _collect_follow_ups(result.tech_top),
        "finance": _collect_follow_ups(result.finance_top),
        "pm": _collect_follow_ups(result.pm_top),
    }

    logger.info(
        f"Report context built: {len(ctx['top_global'])} top, "
        f"ai={len(ctx['ai'])}, tech={len(ctx['tech'])}, "
        f"finance={len(ctx['finance'])}, pm={len(ctx['pm'])}"
    )
    return ctx


def _article_to_dict(article: Article) -> dict:
    """Convert an Article to a plain dict with extra display fields."""
    d = article.model_dump()

    # Add human-readable time
    if article.published_at:
        local = article.published_at.strftime("%Y-%m-%d %H:%M")
        d["published_at_cn"] = local
        d["published_at_relative"] = _relative_time(article.published_at)
    else:
        d["published_at_cn"] = "时间未知"
        d["published_at_relative"] = ""

    # Ensure analysis is a dict or None
    if d.get("analysis") and isinstance(d["analysis"], dict):
        analysis = d["analysis"]
        d["analysis_one_sentence"] = analysis.get("one_sentence_conclusion", "")
        d["analysis_why_important"] = analysis.get("why_important", "")
        d["analysis_impact"] = analysis.get("potential_impact", [])
        d["analysis_follow_up"] = analysis.get("follow_up_points", [])
        d["analysis_insufficient"] = analysis.get("insufficient_info", False)
    else:
        d["analysis_one_sentence"] = ""
        d["analysis_why_important"] = ""
        d["analysis_impact"] = []
        d["analysis_follow_up"] = []
        d["analysis_insufficient"] = True

    # Format score
    d["score_display"] = f"{article.score:.1f}"

    return d


def _relative_time(dt: datetime) -> str:
    """Return a relative time string like '3小时前'."""
    from datetime import timezone

    now = datetime.now(timezone.utc)
    delta = now - dt
    hours = delta.total_seconds() / 3600
    if hours < 1:
        return f"{int(delta.total_seconds() // 60)}分钟前"
    if hours < 24:
        return f"{int(hours)}小时前"
    return f"{int(hours // 24)}天前"


def _build_trend_summary(ctx: dict, now: datetime) -> str:
    """Generate an overall trend summary based on collected data."""
    total = ctx["total_articles"]
    parts = []

    parts.append(f"今日共采集并处理 {total} 篇科技、金融、AI 领域新闻。")

    # Category distribution
    counts = {}
    for cat in ["ai", "tech", "finance", "pm", "general"]:
        counts[cat] = len(ctx.get(cat, []))

    if counts.get("ai", 0) > 0:
        parts.append(f"AI 领域 {counts['ai']} 条重点新闻")
    if counts.get("tech", 0) > 0:
        parts.append(f"科技领域 {counts['tech']} 条重点新闻")
    if counts.get("finance", 0) > 0:
        parts.append(f"金融领域 {counts['finance']} 条重点新闻")
    if counts.get("pm", 0) > 0:
        parts.append(f"产品经理领域 {counts['pm']} 条重点新闻")

    # Try to extract a common theme from AI analysis
    themes = set()
    for cat in ["ai", "tech", "finance", "pm"]:
        for art in ctx.get(cat, []):
            sentence = art.get("analysis_one_sentence", "")
            if sentence and not art.get("analysis_insufficient", True):
                themes.add(sentence[:10])
    if not themes:
        parts.append("整体信息量丰富，覆盖多个热点领域。")

    return "｜".join(parts)


def _build_trends(ctx: dict) -> list[str]:
    """Collect trend observations from article analyses."""
    trends: list[str] = []
    seen = set()

    for cat in ["ai", "tech", "finance", "pm"]:
        for art in ctx.get(cat, []):
            for impact in art.get("analysis_impact", []):
                key = impact.strip()[:30]
                if impact and key not in seen:
                    seen.add(key)
                    trends.append(impact.strip())

    if not trends:
        trends.append("各领域均有重要动态，建议关注后续发展。")

    return trends[:6]  # at most 6 trends


def _collect_follow_ups(articles: list[Article]) -> list[str]:
    """Collect follow-up observation points from a set of articles."""
    points: list[str] = []
    seen = set()

    for art in articles:
        if not art.analysis:
            continue
        analysis = art.analysis if isinstance(art.analysis, dict) else {}
        for point in analysis.get("follow_up_points", []):
            key = point.strip()[:30]
            if point and key not in seen:
                seen.add(key)
                points.append(point.strip())

    return points[:4]  # at most 4 per module

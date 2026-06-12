"""Markdown report renderer — generates a clean daily report in Markdown format."""


def render_markdown(ctx: dict) -> str:
    """Render the entire report as a Markdown string.

    Args:
        ctx: Report context dict from build_report_context().

    Returns:
        Markdown string ready to save as .md file.
    """
    lines: list[str] = []

    _add_header(lines, ctx)
    _add_toc(lines, ctx)
    _add_section(lines, "🔥 今日最重要", ctx.get("top_global", []), ctx["date"])
    _add_section(lines, "🤖 AI 模块", ctx.get("ai", []), ctx["date"])
    _add_section(lines, "💻 科技模块", ctx.get("tech", []), ctx["date"])
    _add_section(lines, "💰 金融模块", ctx.get("finance", []), ctx["date"])
    _add_section(lines, "📱 产品经理模块", ctx.get("pm", []), ctx["date"])
    _add_trends(lines, ctx)
    _add_follow_up(lines, ctx)
    _add_footer(lines, ctx)

    return "\n".join(lines)


def _add_header(lines: list[str], ctx: dict) -> None:
    """Report header with title and date."""
    lines.append(f"# 每日情报简报 · {ctx['date']}")
    lines.append("")
    lines.append(f"> **生成时间**: {ctx['date_cn']}  ｜  **覆盖**: 近3天科技/金融/AI 动态")
    lines.append("")
    lines.append("---")
    lines.append("")


def _add_toc(lines: list[str], ctx: dict) -> None:
    """Table of contents."""
    lines.append("## 📑 目录")
    lines.append("")
    sections = []
    if ctx.get("top_global"):
        sections.append("[🔥 今日最重要](#-今日最重要)")
    for label, key in [("🤖 AI 模块", "ai"), ("💻 科技模块", "tech"), ("💰 金融模块", "finance"), ("📱 产品经理模块", "pm")]:
        if ctx.get(key):
            slug = label.split(" ")[1]
            sections.append(f"[{label}](#-{slug}模块)")
    sections.append("[📊 今日趋势判断](#-今日趋势判断)")
    sections.append("[👀 明日继续跟踪](#-明日继续跟踪)")
    for s in sections:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("---")
    lines.append("")


def _add_section(lines: list[str], title: str, articles: list[dict], date: str) -> None:
    """Add a section with a list of articles."""
    if not articles:
        return

    lines.append(f"## {title}")
    lines.append("")

    for i, art in enumerate(articles, 1):
        score = art.get("score_display", "0")
        source = art.get("source_name", "未知")
        time_rel = art.get("published_at_relative", "")
        title_text = art.get("title", "无标题")
        url = art.get("url", "")

        lines.append(f"### {i}. [{title_text}]({url})")
        lines.append("")
        lines.append(f"- **评分**: `{score}`  ｜ **来源**: {source}  ｜ **时间**: {time_rel}")
        lines.append("")

        # LLM analysis
        analysis_ok = not art.get("analysis_insufficient", True)
        if analysis_ok:
            conclusion = art.get("analysis_one_sentence", "")
            why = art.get("analysis_why_important", "")
            impact = art.get("analysis_impact", [])
            if conclusion:
                lines.append(f"> **一句话结论**: {conclusion}")
                lines.append("")
            if why:
                lines.append(f"> **为什么重要**: {why}")
                lines.append("")
            if impact:
                lines.append("> **可能影响**:")
                for imp in impact:
                    lines.append(f"> - {imp}")
                lines.append("")
        else:
            # Just show summary if available
            summary = art.get("summary", "")
            if summary:
                lines.append(f"> {summary[:200]}")
                lines.append("")

        lines.append("")

    lines.append("---")
    lines.append("")


def _add_trends(lines: list[str], ctx: dict) -> None:
    """Add trend analysis section."""
    lines.append("## 📊 今日趋势判断")
    lines.append("")

    summary = ctx.get("trend_summary", "")
    if summary:
        lines.append(summary)
        lines.append("")

    trends = ctx.get("trends", [])
    if trends:
        lines.append("### 值得关注的影响")
        lines.append("")
        for t in trends:
            lines.append(f"- {t}")
        lines.append("")

    lines.append("---")
    lines.append("")


def _add_follow_up(lines: list[str], ctx: dict) -> None:
    """Add follow-up section with items to watch."""
    lines.append("## 👀 明日继续跟踪")
    lines.append("")

    follow_up = ctx.get("follow_up", {})
    has_any = any(v for v in follow_up.values())

    if not has_any:
        lines.append("> 暂无具体的跟踪建议。")
        lines.append("")
        lines.append("---")
        lines.append("")
        return

    module_labels = {"ai": "AI", "tech": "科技", "finance": "金融", "pm": "产品经理"}
    for key, label in module_labels.items():
        points = follow_up.get(key, [])
        if points:
            lines.append(f"**{label}**")
            for p in points:
                lines.append(f"- {p}")
            lines.append("")

    lines.append("---")
    lines.append("")


def _add_footer(lines: list[str], ctx: dict) -> None:
    """Report footer."""
    lines.append("")
    lines.append("---")
    lines.append(f"*Daily Intelligence Agent · 自动生成于 {ctx['date_cn']}*")
    lines.append("")

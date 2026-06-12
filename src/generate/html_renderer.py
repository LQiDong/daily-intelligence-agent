"""HTML report renderer — generates a mobile-friendly daily report in HTML format.

The HTML is designed for email viewing on mobile devices:
- Single-column layout
- Responsive, max-width 640px
- Clean sans-serif font
- Color-coded category badges
- Collapsible article details
"""


def render_html(ctx: dict) -> str:
    """Render the entire report as a self-contained HTML string.

    Args:
        ctx: Report context dict from build_report_context().

    Returns:
        Complete HTML document string.
    """
    articles_html = _build_all_sections(ctx)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日情报简报 · {ctx['date']}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
    background: #f5f7fa;
    color: #1a1a2e;
    font-size: 15px;
    line-height: 1.6;
    padding: 0;
  }}
  .container {{ max-width: 640px; margin: 0 auto; background: #fff; min-height: 100vh; }}
  .header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    padding: 28px 20px 20px;
    text-align: center;
  }}
  .header h1 {{ font-size: 22px; font-weight: 700; margin-bottom: 6px; }}
  .header p {{ font-size: 13px; opacity: 0.9; }}
  .toc {{ background: #f8f9ff; padding: 16px 20px; font-size: 14px; }}
  .toc a {{ color: #667eea; text-decoration: none; display: block; padding: 3px 0; }}
  .section {{ padding: 20px; border-bottom: 1px solid #eee; }}
  .section:last-child {{ border-bottom: none; }}
  .section-title {{
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 3px solid #667eea;
  }}
  .article {{ margin-bottom: 20px; padding: 14px; background: #fafbff; border-radius: 10px; }}
  .article:last-child {{ margin-bottom: 0; }}
  .article-title {{
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 6px;
    line-height: 1.4;
  }}
  .article-title a {{ color: #1a1a2e; text-decoration: none; }}
  .article-title a:hover {{ color: #667eea; text-decoration: underline; }}
  .article-meta {{ font-size: 12px; color: #888; margin-bottom: 8px; }}
  .badge {{
    display: inline-block;
    padding: 1px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 4px;
  }}
  .badge-score {{ background: #e8f5e9; color: #2e7d32; }}
  .badge-source {{ background: #e3f2fd; color: #1565c0; }}
  .badge-time {{ background: #fff3e0; color: #e65100; }}
  .analysis-box {{
    margin-top: 8px;
    padding: 10px 12px;
    background: #fff;
    border-left: 3px solid #667eea;
    border-radius: 0 6px 6px 0;
    font-size: 13px;
  }}
  .analysis-box .conclusion {{ font-weight: 600; margin-bottom: 4px; }}
  .analysis-box .label {{ color: #667eea; font-weight: 600; }}
  .analysis-box ul {{ margin: 4px 0 0 16px; }}
  .analysis-box li {{ margin-bottom: 2px; }}
  .summary {{ color: #555; font-size: 13px; }}
  .trend-item {{
    padding: 8px 12px;
    margin-bottom: 6px;
    background: #f0f4ff;
    border-radius: 6px;
    font-size: 14px;
  }}
  .follow-up-module {{ margin-bottom: 12px; }}
  .follow-up-module h4 {{ font-size: 14px; color: #667eea; margin-bottom: 6px; }}
  .follow-up-module li {{ font-size: 13px; margin-bottom: 3px; }}
  .footer {{
    text-align: center;
    padding: 20px;
    font-size: 12px;
    color: #aaa;
    background: #f5f7fa;
  }}
  @media (max-width: 480px) {{
    .header {{ padding: 20px 16px 16px; }}
    .header h1 {{ font-size: 19px; }}
    .section {{ padding: 14px; }}
    .article {{ padding: 10px; }}
  }}
</style>
</head>
<body>
<div class="container">
  {_build_header(ctx)}
  {_build_toc_html(ctx)}
  {articles_html}
  {_build_trends_html(ctx)}
  {_build_follow_up_html(ctx)}
  {_build_footer(ctx)}
</div>
</body>
</html>
"""


def _build_header(ctx: dict) -> str:
    return f"""<div class="header">
  <h1>📋 每日情报简报</h1>
  <p>{ctx['date_cn']}  ·  覆盖科技 · 金融 · AI</p>
</div>"""


def _build_toc_html(ctx: dict) -> str:
    items = []
    anchors = {
        "top_global": "今日最重要",
        "ai": "AI 模块",
        "tech": "科技模块",
        "finance": "金融模块",
        "pm": "产品经理模块",
    }
    for key, label in anchors.items():
        if ctx.get(key):
            items.append(f'<a href="#section-{key}">▸ {label}</a>')
    items.append('<a href="#section-trends">▸ 今日趋势判断</a>')
    items.append('<a href="#section-followup">▸ 明日继续跟踪</a>')

    return f'<div class="toc">{"".join(items)}</div>'


def _build_all_sections(ctx: dict) -> str:
    sections = ""
    sections += _build_section_html("🔥 今日最重要", "top_global", ctx.get("top_global", []), ctx)
    sections += _build_section_html("🤖 AI 模块", "ai", ctx.get("ai", []), ctx)
    sections += _build_section_html("💻 科技模块", "tech", ctx.get("tech", []), ctx)
    sections += _build_section_html("💰 金融模块", "finance", ctx.get("finance", []), ctx)
    sections += _build_section_html("📱 产品经理模块", "pm", ctx.get("pm", []), ctx)
    return sections


def _build_section_html(title: str, key: str, articles: list[dict], ctx: dict) -> str:
    if not articles:
        return ""

    articles_html = ""
    for art in articles:
        articles_html += _build_article_html(art)

    return f"""<div class="section" id="section-{key}">
  <div class="section-title">{title}</div>
  {articles_html}
</div>"""


def _build_article_html(art: dict) -> str:
    title = art.get("title", "无标题")
    url = art.get("url", "")
    score = art.get("score_display", "0")
    source = art.get("source_name", "未知")
    time_rel = art.get("published_at_relative", "")
    analysis_ok = not art.get("analysis_insufficient", True)
    conclusion = art.get("analysis_one_sentence", "")
    why = art.get("analysis_why_important", "")
    impact = art.get("analysis_impact", [])
    summary = art.get("summary", "")

    # Analysis block
    analysis_html = ""
    if analysis_ok and (conclusion or why or impact):
        parts = ""
        if conclusion:
            parts += f'<div class="conclusion">💡 {conclusion}</div>'
        if why:
            parts += f'<div><span class="label">🎯 为什么重要：</span>{why}</div>'
        if impact:
            items = "".join(f"<li>{imp}</li>" for imp in impact)
            parts += f'<div><span class="label">📊 可能影响：</span><ul>{items}</ul></div>'
        analysis_html = f'<div class="analysis-box">{parts}</div>'
    elif summary:
        analysis_html = f'<div class="summary">{summary[:200]}</div>'

    return f"""<div class="article">
  <div class="article-title"><a href="{url}" target="_blank">{title}</a></div>
  <div class="article-meta">
    <span class="badge badge-score">{score}分</span>
    <span class="badge badge-source">{source}</span>
    <span class="badge badge-time">{time_rel}</span>
  </div>
  {analysis_html}
</div>"""


def _build_trends_html(ctx: dict) -> str:
    summary = ctx.get("trend_summary", "")
    trends = ctx.get("trends", [])

    if not summary and not trends:
        return ""

    trends_items = "".join(f'<div class="trend-item">📌 {t}</div>' for t in trends)

    return f"""<div class="section" id="section-trends">
  <div class="section-title">📊 今日趋势判断</div>
  {f'<p style="margin-bottom:12px;font-size:14px;color:#555;">{summary}</p>' if summary else ''}
  {trends_items if trends else ''}
</div>"""


def _build_follow_up_html(ctx: dict) -> str:
    follow_up = ctx.get("follow_up", {})
    has_any = any(v for v in follow_up.values())

    if not has_any:
        return ""

    module_labels = {"ai": "🤖 AI", "tech": "💻 科技", "finance": "💰 金融", "pm": "📱 产品经理"}
    modules_html = ""
    for key, label in module_labels.items():
        points = follow_up.get(key, [])
        if points:
            items = "".join(f"<li>{p}</li>" for p in points)
            modules_html += f"""<div class="follow-up-module">
  <h4>{label}</h4>
  <ul>{items}</ul>
</div>"""

    return f"""<div class="section" id="section-followup">
  <div class="section-title">👀 明日继续跟踪</div>
  {modules_html}
</div>"""


def _build_footer(ctx: dict) -> str:
    return f"""<div class="footer">
  <p>Daily Intelligence Agent · 自动生成于 {ctx['date_cn']}</p>
</div>"""

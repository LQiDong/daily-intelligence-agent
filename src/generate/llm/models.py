"""Pydantic models for LLM analysis results."""

from pydantic import BaseModel, Field


class ArticleAnalysis(BaseModel):
    """Structured analysis of a single news article produced by the LLM summarizer."""

    one_sentence_conclusion: str = Field(
        "", description="一句话结论：用一句话概括这篇新闻的核心内容"
    )
    key_facts: list[str] = Field(
        default_factory=list,
        description="核心事实：从原文中提取的客观事实列表，每一条应可在原文中找到对应依据",
    )
    why_important: str = Field(
        "", description="为什么重要：解释这篇新闻为什么值得关注"
    )
    potential_impact: list[str] = Field(
        default_factory=list,
        description="可能影响：事件可能带来的影响，每条不超过 50 字",
    )
    follow_up_points: list[str] = Field(
        default_factory=list,
        description="后续观察点：未来值得持续关注的信号或事件",
    )
    insufficient_info: bool = Field(
        False,
        description="当原文信息不足以做出有意义的分析时设为 True",
    )
    insufficient_reason: str = Field(
        "",
        description="当 insufficient_info=True 时，说明具体缺少哪些信息",
    )

"""ArticleSummarizer — analyzes articles via OpenAI or Anthropic API.

Supports two backends selected via environment variable LLM_PROVIDER:
  - "openai" (default): uses OpenAI Chat Completions API
  - "anthropic": uses Anthropic Messages API

All API calls use httpx with configurable timeout. In mock mode (for tests),
set MOCK_LLM=true to bypass real API calls.
"""

import json
import os
from typing import Any

import httpx
from loguru import logger

from src.config import get_settings
from src.generate.llm.models import ArticleAnalysis
from src.generate.llm.prompts import (
    SUMMARY_SYSTEM_PROMPT,
    build_summary_user_prompt,
)


class ArticleSummarizer:
    """Analyze news articles using a remote LLM API."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider = self.settings.llm_provider  # "openai" or "anthropic"
        self.timeout = self.settings.http_timeout
        self.mock = os.environ.get("MOCK_LLM", "").lower() in ("true", "1", "yes")
        logger.info(
            f"ArticleSummarizer initialized (provider={self.provider}, mock={self.mock})"
        )

    def analyze(self, title: str, summary: str, source_name: str) -> ArticleAnalysis:
        """Analyze a single news article and return structured analysis.

        Args:
            title: Article title
            summary: Article body / description text
            source_name: Source identifier

        Returns:
            ArticleAnalysis with LLM-generated content, or a fallback analysis
            if the API call fails.
        """
        if self.mock:
            return self._mock_analysis(title, summary)

        try:
            user_prompt = build_summary_user_prompt(title, summary, source_name)

            if self.provider == "anthropic":
                raw = self._call_anthropic(user_prompt)
            else:
                raw = self._call_openai(user_prompt)

            return self._parse_response(raw, title)

        except Exception as exc:
            logger.error(f"ArticleSummarizer API call failed for '{title[:40]}': {exc}")
            return ArticleAnalysis(
                insufficient_info=True,
                insufficient_reason=f"分析失败：{exc}",
            )

    def analyze_batch(self, articles: list[dict]) -> list[ArticleAnalysis]:
        """Analyze multiple articles sequentially.

        Args:
            articles: List of dicts with keys title, summary, source_name.

        Returns:
            List of ArticleAnalysis in the same order.
        """
        results: list[ArticleAnalysis] = []
        for art in articles:
            analysis = self.analyze(
                title=art.get("title", ""),
                summary=art.get("summary", ""),
                source_name=art.get("source_name", ""),
            )
            results.append(analysis)
        logger.info(f"Analyzed {len(results)} articles in batch")
        return results

    # ------------------------------------------------------------------
    # OpenAI backend
    # ------------------------------------------------------------------
    def _call_openai(self, user_prompt: str) -> str:
        """Call OpenAI Chat Completions API and return raw text response."""
        api_key = self.settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        url = f"{self.settings.openai_base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        choices = data.get("choices", [])
        if not choices:
            raise ValueError("OpenAI returned empty choices")
        return choices[0].get("message", {}).get("content", "")

    # ------------------------------------------------------------------
    # Anthropic backend
    # ------------------------------------------------------------------
    def _call_anthropic(self, user_prompt: str) -> str:
        """Call Anthropic Messages API and return raw text response."""
        api_key = self.settings.anthropic_api_key
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")

        url = self.settings.anthropic_base_url.rstrip("/") + "/messages"
        payload: dict[str, Any] = {
            "model": self.settings.anthropic_model,
            "system": SUMMARY_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": 1024,
            "temperature": 0.3,
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        content_blocks = data.get("content", [])
        text_parts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
        return "\n".join(text_parts)

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_response(raw: str, title: str) -> ArticleAnalysis:
        """Parse the LLM JSON response into an ArticleAnalysis.

        Handles markdown code fences (```json ... ```) gracefully.
        """
        text = raw.strip()

        # Strip markdown code fences
        if text.startswith("```"):
            # Remove opening fence
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline + 1 :]
            # Remove closing fence
            if text.endswith("```"):
                text = text[:-3].strip()
            elif "```" in text:
                text = text[: text.rfind("```")].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM JSON for '{title[:40]}': {text[:100]}")
            return ArticleAnalysis(
                insufficient_info=True,
                insufficient_reason="LLM 返回的 JSON 格式无法解析",
            )

        return ArticleAnalysis(
            one_sentence_conclusion=data.get("one_sentence_conclusion", ""),
            key_facts=data.get("key_facts", []),
            why_important=data.get("why_important", ""),
            potential_impact=data.get("potential_impact", []),
            follow_up_points=data.get("follow_up_points", []),
            insufficient_info=data.get("insufficient_info", False),
            insufficient_reason=data.get("insufficient_reason", ""),
        )

    # ------------------------------------------------------------------
    # Mock mode for testing
    # ------------------------------------------------------------------
    @staticmethod
    def _mock_analysis(title: str, summary: str) -> ArticleAnalysis:
        """Return a deterministic mock analysis without calling any API."""
        if not title or not summary:
            return ArticleAnalysis(
                insufficient_info=True,
                insufficient_reason="原文标题或正文为空",
            )
        return ArticleAnalysis(
            one_sentence_conclusion=f"这是一篇关于「{title[:30]}」的报道",
            key_facts=[
                f"报道标题为：{title}",
                f"报道来源提供的内容摘要长度为 {len(summary)} 字",
            ],
            why_important=f"该报道涉及 {title[:20]} 相关话题",
            potential_impact=["信息不足：原文未提供足够数据来判断具体影响"],
            follow_up_points=["建议关注该话题的后续报道以获取更多细节"],
            insufficient_info=False,
            insufficient_reason="",
        )

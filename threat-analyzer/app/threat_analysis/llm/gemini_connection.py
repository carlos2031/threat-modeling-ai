"""Gemini LLM connection - lazy proxy to ChatGoogleGenerativeAI."""

import json
import re
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from threat_modeling_shared.logging import get_logger

from app.config import Settings
from app.threat_analysis.llm.base import LLMConnection

logger = get_logger("llm.gemini")


class GeminiConnection(LLMConnection):
    """Gemini connection - instantiated only when used."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm: ChatGoogleGenerativeAI | None = None

    @property
    def name(self) -> str:
        return "Gemini"

    def _ensure_llm(self) -> ChatGoogleGenerativeAI | None:
        """Lazy init - only create client when first used."""
        if self._llm is not None:
            return self._llm
        if not self.is_configured():
            return None
        try:
            self._llm = ChatGoogleGenerativeAI(
                model=self._settings.primary_model,
                temperature=self._settings.llm_temperature,
                google_api_key=self._settings.google_api_key,
            )
            logger.info(
                "Gemini connection initialized: %s", self._settings.primary_model
            )
            return self._llm
        except Exception as e:
            logger.error("Gemini init failed: %s", e)
            return None

    def is_configured(self) -> bool:
        return bool(self._settings.google_api_key)

    def _parse_json(self, text: str) -> dict[str, Any]:
        if not text:
            return {
                "error": "Empty response",
                "error_type": "empty",
                "service": self.name,
            }
        text = text.strip()
        pairs = [("{", "}"), ("[", "]")]
        pairs.sort(key=lambda p: (text.find(p[0]) if text.find(p[0]) != -1 else float("inf")))
        for start, end in pairs:
            idx = text.find(start)
            if idx != -1:
                depth = 0
                for i, c in enumerate(text[idx:], idx):
                    if c == start:
                        depth += 1
                    elif c == end:
                        depth -= 1
                        if depth == 0:
                            try:
                                return json.loads(text[idx : i + 1])
                            except json.JSONDecodeError:
                                pass
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        return {
            "error": "Invalid JSON response",
            "error_type": "invalid_json",
            "service": self.name,
        }

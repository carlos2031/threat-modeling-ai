"""OpenAI LLM connection - lazy proxy to ChatOpenAI."""

import json
from typing import Any

from langchain_openai import ChatOpenAI
from threat_modeling_shared.logging import get_logger

from app.config import Settings
from app.threat_analysis.llm.base import LLMConnection

logger = get_logger("llm.openai")


class OpenAIConnection(LLMConnection):
    """OpenAI connection - instantiated only when used."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm: ChatOpenAI | None = None

    @property
    def name(self) -> str:
        return "OpenAI"

    def _ensure_llm(self) -> ChatOpenAI | None:
        if self._llm is not None:
            return self._llm
        if not self.is_configured():
            return None
        try:
            self._llm = ChatOpenAI(
                model=self._settings.fallback_model,
                temperature=self._settings.llm_temperature,
                api_key=self._settings.openai_api_key,
            )
            logger.info(
                "OpenAI connection initialized: %s", self._settings.fallback_model
            )
            return self._llm
        except Exception as e:
            logger.error("OpenAI init failed: %s", e)
            return None

    def is_configured(self) -> bool:
        return bool(self._settings.openai_api_key)

    def _parse_json(self, text: str) -> dict[str, Any]:
        if not text:
            return {
                "error": "Empty response",
                "error_type": "empty",
                "service": self.name,
            }
        text = text.strip().replace("```json", "").replace("```", "").strip()
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
        return {
            "error": "Invalid JSON response",
            "error_type": "invalid_json",
            "service": self.name,
        }

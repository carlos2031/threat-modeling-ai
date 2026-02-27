"""Base agent with common LLM utilities."""

import json
import re
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel
from threat_modeling_shared.logging import get_logger

from app.threat_analysis.exceptions import JSONParsingError

T = TypeVar("T", bound=BaseModel)

logger = get_logger("agents.base")


class BaseAgent(ABC):
    """Abstract base class for all LLM-based agents."""

    @abstractmethod
    async def analyze(self, *args: Any, **kwargs: Any) -> Any:
        """Run the agent's analysis. Implemented by subclasses."""
        pass  # pragma: no cover

    def parse_json_response(
        self,
        content: str,
        *,
        default: Any = None,
        raise_on_error: bool = False,
    ) -> Any:
        """Parse JSON from LLM response content.

        Handles common LLM response patterns:
        - Raw JSON
        - JSON wrapped in ```json code blocks
        - JSON wrapped in ``` code blocks

        Args:
            content: The raw LLM response content.
            default: Value to return if parsing fails (when raise_on_error=False).
            raise_on_error: If True, raise JSONParsingError on failure.

        Returns:
            Parsed JSON data or default value.

        Raises:
            JSONParsingError: If raise_on_error=True and parsing fails.
        """
        if not content:
            if raise_on_error:
                raise JSONParsingError("Empty content", "Content is empty or None")
            return default

        # Try multiple extraction patterns
        json_content = self._extract_json_content(content)

        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.warning("JSON parsing failed: %s", str(e))
            if raise_on_error:
                raise JSONParsingError(content, str(e)) from e
            return default

    def _extract_json_content(self, content: str) -> str:
        """Extract JSON content from various formats.

        Args:
            content: Raw content that may contain JSON.

        Returns:
            Extracted JSON string.
        """
        content = content.strip()

        # Pattern 1: ```json ... ```
        match = re.search(r"```json\s*([\s\S]*?)\s*```", content)
        if match:
            return match.group(1).strip()

        # Pattern 2: ``` ... ``` (generic code block)
        match = re.search(r"```\s*([\s\S]*?)\s*```", content)
        if match:
            potential_json = match.group(1).strip()
            if potential_json.startswith(("{", "[")):
                return potential_json

        # Pattern 3: Find JSON array or object directly
        # Look for first { or [ and match to closing brace/bracket
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start_idx = content.find(start_char)
            if start_idx != -1:
                # Find matching closing bracket
                depth = 0
                in_string = False
                escape_next = False

                for i, char in enumerate(content[start_idx:], start=start_idx):
                    if escape_next:
                        escape_next = False
                        continue

                    if char == "\\":
                        escape_next = True
                        continue

                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue

                    if in_string:
                        continue

                    if char == start_char:
                        depth += 1
                    elif char == end_char:
                        depth -= 1
                        if depth == 0:
                            return content[start_idx : i + 1]

        # No extraction worked, return as-is
        return content

    def validate_with_schema(
        self,
        data: dict[str, Any] | list[Any],
        schema: type[T],
    ) -> T | list[T] | None:
        """Validate parsed data against a Pydantic schema.

        Args:
            data: The parsed JSON data.
            schema: The Pydantic model class to validate against.

        Returns:
            Validated model instance(s) or None if validation fails.
        """
        try:
            if isinstance(data, list):
                return [schema.model_validate(item) for item in data]
            return schema.model_validate(data)
        except Exception as e:
            logger.warning("Schema validation failed: %s", str(e))
            return None

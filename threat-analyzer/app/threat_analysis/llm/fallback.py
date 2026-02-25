"""Fallback runner - try LLMs in order, validate, return first success."""

import json
import time
from collections.abc import Callable
from typing import Any

from threat_modeling_shared.logging import get_logger

from app.threat_analysis.llm.base import LLMConnection

logger = get_logger("llm.fallback")


def is_error_result(result: dict[str, Any]) -> bool:
    """Check if result indicates an error."""
    return "error" in result


def _validation_check(
    validator: Callable[[Any], bool],
    result: Any,
    conn_name: str,
) -> tuple[bool, Any]:
    """Run validator on result; return (True, result) on success, (False, err_info) on failure.

    If validator raises, the exception propagates (caught by caller's except).
    """
    if validator(result):
        return True, result
    if isinstance(result, dict):
        err_info = (
            result if isinstance(result.get("error"), str) else {"error": str(result)}
        )
    else:
        err_info = {"error": f"Validation failed for result type {type(result).__name__}"}
    return False, {"engine": conn_name, **err_info}


async def run_vision_with_fallback(
    connections: list[type[LLMConnection]],
    settings: Any,
    prompt: str,
    image_bytes: bytes,
    cache_get: Callable[[str, ...], Any | None] | None = None,
    cache_set: Callable[[str, Any, ...], None] | None = None,
    cache_key_prefix: str = "diagram",
    validate: Callable[[dict[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Try each connection in order; return first valid result or aggregated errors.

    Args:
        connections: List of LLMConnection classes (not instances).
        settings: Settings to pass to each connection.
        prompt: Vision prompt.
        image_bytes: Image bytes.
        cache_get: Optional cache getter (prefix, *args) -> value or None.
        cache_set: Optional cache setter (prefix, value, *args).
        cache_key_prefix: Prefix for cache key.
        validate: Optional validator(result) -> bool. Default: not is_error_result.

    Returns:
        Valid result dict or {"error": str, "engine_errors": list}.
    """
    validator = validate or (lambda r: not is_error_result(r))

    # Check cache
    if cache_get:
        cached = cache_get(cache_key_prefix, prompt, image_bytes)
        if cached is not None and validator(cached):
            logger.info("Returning cached LLM result")
            return cached

    errors: list[dict[str, Any]] = []
    for conn_class in connections:
        conn = conn_class(settings)
        logger.info("Trying LLM: %s (vision, waiting...)", conn.name)
        try:
            start = time.perf_counter()
            result = await conn.invoke_vision(prompt, image_bytes)
            elapsed = time.perf_counter() - start
            ok, value = _validation_check(validator, result, conn.name)
            if ok:
                logger.info("Success with %s in %.2fs", conn.name, elapsed)
                if cache_set:
                    cache_set(cache_key_prefix, value, prompt, image_bytes)
                return value
            logger.warning("LLM %s: validation failed after %.2fs", conn.name, elapsed)
            errors.append(value)
        except Exception as e:
            errors.append(
                {"engine": conn.name, "error": str(e), "error_type": "exception"}
            )
            logger.warning("%s failed: %s", conn.name, e)

    return {
        "error": "All LLM providers failed",
        "engine_errors": errors,
    }


async def run_text_with_fallback(
    connections: list[type[LLMConnection]],
    settings: Any,
    messages: list[dict[str, str]],
    cache_get: Callable[[str, ...], Any | None] | None = None,
    cache_set: Callable[[str, Any, ...], None] | None = None,
    cache_key_prefix: str = "text",
    validate: Callable[[dict[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """Try each connection for text-only invocation."""
    validator = validate or (lambda r: not is_error_result(r))

    if cache_get:
        key = json.dumps(messages, sort_keys=True)
        cached = cache_get(cache_key_prefix, key)
        if cached is not None and validator(cached):
            logger.info("Returning cached LLM result")
            return cached

    errors: list[dict[str, Any]] = []
    for conn_class in connections:
        conn = conn_class(settings)
        logger.info("Trying LLM: %s (text, waiting...)", conn.name)
        try:
            start = time.perf_counter()
            result = await conn.invoke_text(messages)
            elapsed = time.perf_counter() - start
            ok, value = _validation_check(validator, result, conn.name)
            if ok:
                logger.info("Success with %s in %.2fs", conn.name, elapsed)
                if cache_set:
                    cache_set(
                        cache_key_prefix, value, json.dumps(messages, sort_keys=True)
                    )
                return value
            logger.warning("LLM %s: validation failed after %.2fs", conn.name, elapsed)
            errors.append(value)
        except Exception as e:
            errors.append(
                {"engine": conn.name, "error": str(e), "error_type": "exception"}
            )
            logger.warning("LLM %s failed with exception: %s", conn.name, e)

    return {"error": "All LLM providers failed", "engine_errors": errors}

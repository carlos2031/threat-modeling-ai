"""Abstração de cache — backend plugável (ex.: Redis)."""

from typing import Any, Protocol


class CacheBackend(Protocol):
    """Protocol for cache backends (Redis, memory, etc.)."""

    def get(self, key: str) -> str | None:
        """Return value for key or None if missing."""
        ...

    def set(self, key: str, value: str, ttl_seconds: int = 0) -> None:
        """Store value for key. ttl_seconds=0 means no expiry."""
        ...


class RedisCacheBackend:
    """Redis-backed cache. Requires 'redis' package."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        self._redis_url = redis_url
        self._client: Any = None

    def _get_client(self):
        if self._client is None:
            import redis

            self._client = redis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client

    def get(self, key: str) -> str | None:
        try:
            return self._get_client().get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl_seconds: int = 0) -> None:
        try:
            client = self._get_client()
            if ttl_seconds > 0:
                client.setex(key, ttl_seconds, value)
            else:
                client.set(key, value)
        except Exception:
            pass


def get_cache_backend(redis_url: str = "redis://localhost:6379/0") -> CacheBackend:
    """Retorna o backend de cache (Redis). Trocar implementação aqui para outro backend."""
    return RedisCacheBackend(redis_url=redis_url)

"""Configuration for threat-service.

DB and Redis come from shared BaseSettings (database_url, redis_url).
Celery uses redis_url from env; cache usage should go through shared get_cache_backend.
"""

from functools import lru_cache
from pathlib import Path

from threat_modeling_shared.config import BaseSettings


class Settings(BaseSettings):
    """Threat Modeling API settings — extends shared BaseSettings (database_url, redis_url)."""

    # API (override defaults)
    app_name: str = "Threat Modeling API"
    app_version: str = "1.0.0"
    cors_origins_raw: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:80"
    )

    # Environment
    environment: str = "development"

    # Database: from shared (env DATABASE_URL). Empty = service does not use DB.
    database_url: str = "postgresql://postgres:postgres@localhost:5432/threat_modeling"

    # File storage (UPLOAD_DIR=uploads para Docker; media/ local)
    upload_dir: Path = Path("uploads")
    max_upload_size_mb: int = 10

    # threat-analyzer service URL (called by Celery worker)
    analyzer_url: str = "http://threat-analyzer:8000"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()

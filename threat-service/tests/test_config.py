"""Tests for app.config."""

from pathlib import Path

from app.config import Settings, get_settings


def test_settings_defaults(monkeypatch):
    """Settings has expected defaults."""
    monkeypatch.setenv("APP_NAME", "Threat Modeling API")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/threat_modeling"
    )
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    get_settings.cache_clear()
    s = Settings()
    assert s.app_name == "Threat Modeling API"
    assert s.app_version == "1.0.0"
    assert "postgresql://" in s.database_url and "threat_modeling" in s.database_url
    assert s.upload_dir == Path("media")
    assert s.max_upload_size_mb == 10
    assert s.analyzer_url == "http://threat-analyzer:8000"
    assert s.redis_url == "redis://localhost:6379/0"


def test_max_upload_size_bytes():
    """max_upload_size_bytes returns correct value."""
    s = Settings(max_upload_size_mb=5)
    assert s.max_upload_size_bytes == 5 * 1024 * 1024


def test_get_settings_cached():
    """get_settings returns same instance (cached)."""
    a = get_settings()
    b = get_settings()
    assert a is b

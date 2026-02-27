"""Pytest fixtures for threat-service tests."""

import os
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

# Ensure threat-service/app is on path (must be before app imports)
_root = Path(__file__).resolve().parent.parent
if str(_root) not in (os.environ.get("PYTHONPATH") or "").split(os.pathsep):
    sys.path.insert(0, str(_root))

from app.config import get_settings  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

# Use test database URL; defaults to same as dev with _test suffix
# For CI: set TEST_DATABASE_URL=postgresql://postgres:postgres@postgres:5432/threat_modeling_test
# Requires PostgreSQL running (make run) or createdb threat_modeling_test
settings = get_settings()
TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    settings.database_url.replace("/threat_modeling", "/threat_modeling_test"),
)

# Temp dir for uploads in tests (avoid polluting project)
TEST_UPLOAD_DIR = Path(tempfile.mkdtemp(prefix="tma_test_uploads_"))


@pytest.fixture(scope="session")
def engine():
    """Create test engine. Skips tests if PostgreSQL is not available."""
    try:
        _engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
        Base.metadata.create_all(bind=_engine)
        return _engine
    except OperationalError as e:
        pytest.skip(
            f"PostgreSQL not available: {e}. "
            "Run 'make run' or 'createdb threat_modeling_test' and set TEST_DATABASE_URL."
        )


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(engine):
    """Test client with overridden DB dependency."""
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def use_test_upload_dir(monkeypatch):
    """Use temp dir for uploads in all tests."""
    monkeypatch.setattr(settings, "upload_dir", TEST_UPLOAD_DIR)
    TEST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield


@pytest.fixture
def sample_png_bytes():
    """Minimal valid PNG bytes for upload tests."""
    return (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.fixture
def client_no_db(monkeypatch):
    """Test client without PostgreSQL (dependency override get_db for router unit tests)."""
    from unittest.mock import MagicMock

    mock_engine = MagicMock()
    mock_db = MagicMock()

    def mock_get_db():
        try:
            yield mock_db
        finally:
            pass

    monkeypatch.setattr("app.main.engine", mock_engine)
    monkeypatch.setattr("app.database.engine", mock_engine)
    app.dependency_overrides[get_db] = mock_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)

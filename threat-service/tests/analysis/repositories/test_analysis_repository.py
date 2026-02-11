"""Unit tests for app.analysis.repositories.analysis_repository."""

import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.analysis.models import Analysis, AnalysisStatus
from app.analysis.repositories.analysis_repository import AnalysisRepository


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy session."""
    return MagicMock()


@pytest.fixture
def repository(mock_db):
    """AnalysisRepository with mocked settings."""
    with patch("app.analysis.repositories.analysis_repository.get_settings") as m:
        s = MagicMock()
        s.upload_dir = Path("/tmp/test_uploads_tma")
        s.upload_dir.mkdir(parents=True, exist_ok=True)
        m.return_value = s
        repo = AnalysisRepository(mock_db)
        repo._upload_dir = Path("/tmp/test_uploads_tma")
        yield repo


class TestAnalysisRepository:
    def test_next_code_format(self, repository, mock_db):
        """Generated code has format TMA- + 8 digits."""
        mock_db.execute.return_value.scalars().first.return_value = None
        code = repository._next_code()
        assert code.startswith("TMA-")
        assert len(code) == len("TMA-") + 8
        assert code[4:].isdigit()

    def test_next_code_retries_on_collision(self, repository, mock_db):
        """When generated code exists, retries until unique."""
        existing = Analysis(
            code="TMA-12345678",
            id=uuid.uuid4(),
            image_path="x",
            status=AnalysisStatus.EM_ABERTO,
        )
        # First call returns existing, second returns None (unique)
        mock_db.execute.return_value.scalars().first.side_effect = [
            existing,
            None,
        ]
        code = repository._next_code()
        assert code.startswith("TMA-") and code[4:].isdigit()

    def test_save_image_png(self, repository):
        """PNG bytes save with .png extension."""
        png = b"\x89PNG\r\n\x1a\nxxxx"
        aid = uuid.uuid4()
        name = repository._save_image(png, aid)
        assert name.endswith(".png")
        assert str(aid) in name

    def test_save_image_jpeg(self, repository):
        """JPEG bytes save with .jpg extension."""
        jpeg = b"\xff\xd8\xff"
        aid = uuid.uuid4()
        name = repository._save_image(jpeg, aid)
        assert name.endswith(".jpg")

    def test_save_image_webp(self, repository):
        """WEBP bytes save with .webp extension."""
        webp = b"xxxxxxxxWEBPxxxx"
        aid = uuid.uuid4()
        name = repository._save_image(webp, aid)
        assert name.endswith(".webp")

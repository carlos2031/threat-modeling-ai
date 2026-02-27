"""Unit tests for app.analysis.services.analysis_processing_service."""

import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.analysis.models import Analysis, AnalysisStatus
from app.analysis.services.analysis_processing_service import AnalysisProcessingService


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def service(mock_db):
    return AnalysisProcessingService(mock_db)


class TestAnalysisProcessingService:
    """Tests for AnalysisProcessingService.process."""

    def test_process_analysis_not_found(self, service, mock_db):
        """Returns error dict when analysis not found."""
        with patch.object(service._analysis_repo, "get_by_id", return_value=None):
            result = service.process(uuid.uuid4())
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_process_analysis_already_done(self, service):
        """Returns skipped when analysis already ANALISADO."""
        a = MagicMock()
        a.status = AnalysisStatus.ANALISADO
        with patch.object(service._analysis_repo, "get_by_id", return_value=a):
            result = service.process(uuid.uuid4())
        assert "skipped" in result

    def test_process_analysis_failed_already(self, service):
        """Returns skipped when analysis already FALHOU."""
        a = MagicMock()
        a.status = AnalysisStatus.FALHOU
        with patch.object(service._analysis_repo, "get_by_id", return_value=a):
            result = service.process(uuid.uuid4())
        assert "skipped" in result

    def test_process_image_not_found(self, service):
        """Returns error when image file not found."""
        a = MagicMock()
        a.status = AnalysisStatus.EM_ABERTO
        a.image_path = "x.png"
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        with patch.object(service._analysis_repo, "get_by_id", return_value=a):
            with patch.object(service._analysis_repo, "get_image_path", return_value=None):
                result = service.process(uuid.uuid4())
        assert "error" in result
        assert "image" in result["error"].lower()

    def test_process_success(self, service):
        """Returns success dict when threat-analyzer responds OK."""
        aid = uuid.uuid4()
        a = MagicMock()
        a.id = aid
        a.status = AnalysisStatus.EM_ABERTO
        a.code = "TMA-001"
        a.image_path = "x.png"
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        img_path = MagicMock()
        img_path.exists.return_value = True
        img_path.read_bytes.return_value = b"\x89PNG"
        img_path.suffix = ".png"
        analyzer_result = {"threats": [{}], "risk_level": "Médio"}
        with patch.object(service._analysis_repo, "get_by_id", return_value=a):
            with patch.object(service._analysis_repo, "get_image_path", return_value=img_path):
                with patch("app.analysis.services.analysis_service.httpx") as mock_httpx:
                    resp = MagicMock()
                    resp.raise_for_status = MagicMock()
                    resp.json.return_value = analyzer_result
                    mock_httpx.Client.return_value.__enter__.return_value.post.return_value = resp
                    result = service.process(aid)
        assert result.get("status") == "ANALISADO"
        assert result.get("threat_count") == 1
        assert result.get("risk_level") == "Médio"

    def test_process_http_error(self, service):
        """Returns error when threat-analyzer returns HTTP error."""
        import httpx

        a = MagicMock()
        a.status = AnalysisStatus.EM_ABERTO
        a.image_path = "x.png"
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        img_path = MagicMock()
        img_path.exists.return_value = True
        img_path.read_bytes.return_value = b"\x89PNG"
        img_path.suffix = ".png"
        req = MagicMock()
        resp = MagicMock()
        resp.status_code = 500
        resp.text = "Internal Server Error"
        err = httpx.HTTPStatusError("500", request=req, response=resp)
        resp.raise_for_status.side_effect = err
        with patch.object(service._analysis_repo, "get_by_id", return_value=a):
            with patch.object(service._analysis_repo, "get_image_path", return_value=img_path):
                mock_client = MagicMock()
                mock_client.post.return_value = resp
                with patch("app.analysis.services.analysis_service.httpx.Client") as mock_cls:
                    mock_cls.return_value.__enter__.return_value = mock_client
                    result = service.process(uuid.uuid4())
        assert "error" in result

    def test_process_generic_exception(self, service):
        """Returns error when threat-analyzer raises generic Exception."""
        a = MagicMock()
        a.status = AnalysisStatus.EM_ABERTO
        a.image_path = "x.png"
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        img_path = MagicMock()
        img_path.exists.return_value = True
        img_path.read_bytes.return_value = b"\x89PNG"
        img_path.suffix = ".png"
        resp = MagicMock()
        resp.raise_for_status.side_effect = OSError("Connection refused")
        with patch.object(service._analysis_repo, "get_by_id", return_value=a):
            with patch.object(service._analysis_repo, "get_image_path", return_value=img_path):
                mock_client = MagicMock()
                mock_client.post.return_value = resp
                with patch("app.analysis.services.analysis_service.httpx.Client") as mock_cls:
                    mock_cls.return_value.__enter__.return_value = mock_client
                    result = service.process(uuid.uuid4())
        assert "error" in result

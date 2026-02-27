"""Unit tests for app.threat_analysis.service."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.config import get_settings
from app.threat_analysis.service import ThreatModelService


@pytest.fixture
def sample_png_bytes():
    return (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


class TestThreatModelService:
    def test_run_full_analysis_returns_response(self, sample_png_bytes):
        """Run full pipeline with mocked agents and guardrail so tests do not call LLM."""
        settings = get_settings()
        service = ThreatModelService(settings)
        diagram_data = {
            "model": "test-model",
            "components": [
                {"id": "c1", "type": "Server", "name": "API", "description": None}
            ],
            "connections": [
                {
                    "from": "c1",
                    "to": "c2",
                    "protocol": "HTTPS",
                    "description": None,
                    "encrypted": True,
                }
            ],
        }
        threats = [
            {
                "component_id": "c1",
                "threat_type": "Spoofing",
                "description": "Test threat",
                "mitigation": "Use auth",
                "dread_score": 4.0,
                "dread_details": None,
            }
        ]
        mock_diagram = AsyncMock(return_value=diagram_data)
        mock_stride = AsyncMock(return_value=threats)
        mock_dread = AsyncMock(return_value=threats)
        with (
            patch(
                "app.threat_analysis.service.validate_architecture_diagram",
                new_callable=AsyncMock,
            ),
            patch("app.threat_analysis.service.DiagramAgent") as DiagramCls,
            patch("app.threat_analysis.service.StrideAgent") as StrideCls,
            patch("app.threat_analysis.service.DreadAgent") as DreadCls,
        ):
            DiagramCls.return_value.analyze = mock_diagram
            StrideCls.return_value.analyze = mock_stride
            DreadCls.return_value.analyze = mock_dread
            result = asyncio.run(service.run_full_analysis(sample_png_bytes))
        assert result.model_used == "test-model"
        assert result.risk_score >= 0 and result.risk_score <= 10
        assert result.risk_level is not None
        assert result.threat_count == 1
        assert result.component_count == 1

    def test_calculate_risk_score_empty(self):
        settings = get_settings()
        service = ThreatModelService(settings)
        assert service._calculate_risk_score([]) == 0.0

    def test_parse_components_handles_invalid(self):
        settings = get_settings()
        service = ThreatModelService(settings)
        result = service._parse_components(
            [{"id": "x", "type": "S", "name": "n"}, {"id": 123}]
        )
        assert len(result) == 1
        assert result[0].id == "x"

    def test_parse_connections_handles_invalid(self):
        settings = get_settings()
        service = ThreatModelService(settings)
        result = service._parse_connections([{"from": "a", "to": "b"}])
        assert len(result) == 1
        assert result[0].from_id == "a"

    def test_parse_threats_handles_invalid(self):
        settings = get_settings()
        service = ThreatModelService(settings)
        result = service._parse_threats(
            [
                {
                    "component_id": "c1",
                    "threat_type": "S",
                    "description": "d",
                    "mitigation": "m",
                },
            ]
        )
        assert len(result) == 1
        assert result[0].component_id == "c1"

    def test_parse_threats_deduplicates_by_type_and_description(self):
        """Duplicate threats (same threat_type + normalized description) are kept only once."""
        settings = get_settings()
        service = ThreatModelService(settings)
        duplicate_threat = {
            "component_id": "c1",
            "threat_type": "Information Disclosure",
            "description": "Data in transit could be intercepted if HTTPS is not properly configured.",
            "mitigation": "Ensure TLS is used and certificates are valid.",
            "dread_score": 7.4,
            "dread_details": None,
        }
        threats = [duplicate_threat.copy(), duplicate_threat.copy(), duplicate_threat.copy()]
        result = service._parse_threats(threats)
        assert len(result) == 1
        assert result[0].threat_type == "Information Disclosure"
        assert result[0].dread_score == 7.4

    def test_threat_dedup_key_normalizes_type_and_description(self):
        """_threat_dedup_key normalizes threat_type and description for consistent dedup."""
        key1 = ThreatModelService._threat_dedup_key(
            {"threat_type": "  information disclosure  ", "description": "  Foo   Bar  "}
        )
        key2 = ThreatModelService._threat_dedup_key(
            {"threat_type": "Information Disclosure", "description": "foo bar"}
        )
        assert key1 == key2

    def test_parse_connections_logs_warning_on_validation_error(self, caplog):
        """Trigger except in _parse_connections (invalid Connection data)."""
        settings = get_settings()
        service = ThreatModelService(settings)
        result = service._parse_connections(
            [
                {"from": "a", "to": "b"},
                {"from": "x", "to": "y", "encrypted": "not_a_bool"},
            ]
        )
        assert len(result) == 1
        assert "Failed to parse connection" in caplog.text

    def test_parse_threats_logs_warning_on_validation_error(self, caplog):
        """Trigger except in _parse_threats (invalid Threat data)."""
        settings = get_settings()
        service = ThreatModelService(settings)
        result = service._parse_threats(
            [
                {
                    "component_id": "c1",
                    "threat_type": "S",
                    "description": "d",
                    "mitigation": "m",
                },
                {
                    "component_id": "c2",
                    "threat_type": "T",
                    "description": "d",
                    "mitigation": "m",
                    "dread_details": "invalid",
                },
            ]
        )
        assert len(result) == 1
        assert "Failed to parse threat" in caplog.text

    def test_get_threat_model_service_returns_singleton(self):
        """get_threat_model_service is cached and returns ThreatModelService."""
        from app.threat_analysis.service import get_threat_model_service

        get_threat_model_service.cache_clear()
        svc = get_threat_model_service()
        assert isinstance(svc, ThreatModelService)
        assert get_threat_model_service() is svc

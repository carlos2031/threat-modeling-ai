"""Threat Analysis Controller - business logic for diagram analysis."""

from threat_modeling_shared.logging import get_logger

from app.config import Settings
from app.threat_analysis.exceptions import InvalidFileTypeError, ThreatModelingError
from app.threat_analysis.schemas import AnalysisResponse
from app.threat_analysis.service import ThreatModelService

logger = get_logger("controller")


class ThreatAnalysisController:
    """Controller for threat analysis operations."""

    def __init__(self, service: ThreatModelService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    async def analyze(
        self,
        image_bytes: bytes,
        content_type: str | None = None,
    ) -> AnalysisResponse:
        """Execute full threat analysis on an architecture diagram.

        Args:
            image_bytes: Raw image content.
            content_type: MIME type of the upload (e.g. image/png). Validated against allowed_image_types.

        Returns:
            Complete analysis response with components, threats, and risk.

        Raises:
            InvalidFileTypeError: If content_type is not allowed.
            ThreatModelingError: If analysis fails.
        """
        self._validate_input(image_bytes, content_type)

        logger.info("Running analysis: size=%d bytes", len(image_bytes))

        result = await self._service.run_full_analysis(image_bytes)
        return result

    def _validate_input(
        self, image_bytes: bytes, content_type: str | None = None
    ) -> None:
        """Validate input before analysis (file type, size, non-empty)."""
        if (
            content_type is not None
            and content_type not in self._settings.allowed_image_types
        ):
            raise InvalidFileTypeError(content_type, self._settings.allowed_image_types)

        if not image_bytes or len(image_bytes) == 0:
            raise ThreatModelingError("Empty image content", details={})

        if len(image_bytes) > self._settings.max_upload_size_bytes:
            raise ThreatModelingError(
                f"File too large. Maximum size: {self._settings.max_upload_size_mb}MB",
                details={"max_bytes": self._settings.max_upload_size_bytes},
            )

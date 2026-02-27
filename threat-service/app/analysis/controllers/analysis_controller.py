"""Analysis controller — orquestração e regras de negócio."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.analysis.models import AnalysisStatus
from app.analysis.repositories.analysis_repository import AnalysisRepository
from app.analysis.schemas import (
    AnalysisCreateResponse,
    AnalysisDetailResponse,
    AnalysisFilter,
    AnalysisListResponse,
    AnalysisStatusEnum,
)
from app.analysis.validators.analysis_validator import AnalysisValidator


class AnalysisController:
    """Controller para operações de analysis."""

    def __init__(self, db: Session) -> None:
        self._repository = AnalysisRepository(db)
        self._validator = AnalysisValidator()

    def create_analysis(
        self, image_bytes: bytes, filename: str
    ) -> AnalysisCreateResponse:
        """Cria nova analysis a partir do upload. Valida, persiste e retorna response."""
        self._validator.validate_upload_file(
            content_type=self._guess_content_type(image_bytes),
            size=len(image_bytes),
        )
        analysis = self._repository.create(image_bytes, filename or "")
        return AnalysisCreateResponse(
            id=str(analysis.id),
            code=analysis.code,
            status=AnalysisStatusEnum(analysis.status.value),
            created_at=analysis.created_at,
            image_url=f"/api/v1/analyses/{analysis.id}/image",
        )

    def _guess_content_type(self, image_bytes: bytes) -> str:
        """Infere content-type pelos magic bytes."""
        if len(image_bytes) >= 8 and image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        if len(image_bytes) >= 12 and image_bytes[8:12] == b"WEBP":
            return "image/webp"
        if len(image_bytes) >= 2 and image_bytes[:2] == b"\xff\xd8":
            return "image/jpeg"
        return "image/png"

    def list_analyses(self, filters: AnalysisFilter) -> list[AnalysisListResponse]:
        """
        Lista analyses com filtros (código, status, range de datas).
        A paginação é aplicada no router via fastapi-pagination.
        """
        status_enum = (
            AnalysisStatus(filters.status.value) if filters.status is not None else None
        )
        analyses = self._repository.list_all(
            status=status_enum,
            code_substring=filters.code,
            created_at_from=filters.created_at_from,
            created_at_to=filters.created_at_to,
            limit=2000,
            offset=0,
        )
        return [
            AnalysisListResponse(
                id=str(a.id),
                code=a.code,
                status=AnalysisStatusEnum(a.status.value),
                created_at=a.created_at,
                image_url=f"/api/v1/analyses/{a.id}/image",
                risk_level=a.result.get("risk_level") if a.result else None,
                risk_score=a.result.get("risk_score") if a.result else None,
                threat_count=len(a.result.get("threats", [])) if a.result else None,
            )
            for a in analyses
        ]

    def get_analysis(self, analysis_id: uuid.UUID) -> AnalysisDetailResponse | None:
        """Retorna detail da analysis ou None se não existir."""
        analysis = self._repository.get_by_id(analysis_id)
        if not analysis:
            return None
        return AnalysisDetailResponse(
            id=str(analysis.id),
            code=analysis.code,
            status=AnalysisStatusEnum(analysis.status.value),
            created_at=analysis.created_at,
            started_at=analysis.started_at,
            finished_at=analysis.finished_at,
            image_url=f"/api/v1/analyses/{analysis.id}/image",
            processing_logs=analysis.processing_logs,
            error_message=analysis.error_message,
            result=analysis.result,
        )

    def get_analysis_or_404(self, analysis_id: uuid.UUID) -> AnalysisDetailResponse:
        """Retorna detail ou levanta 404."""
        detail = self.get_analysis(analysis_id)
        if not detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found",
            )
        return detail

    def get_image_path(self, analysis_id: uuid.UUID) -> Path | None:
        """Retorna caminho da imagem ou None."""
        return self._repository.get_image_path(analysis_id)

    def get_image_path_and_media_type(
        self, analysis_id: uuid.UUID
    ) -> tuple[Path | None, str | None]:
        """Retorna (caminho da imagem, media_type) ou (None, None) se não existir."""
        path = self._repository.get_image_path(analysis_id)
        if not path or not path.exists():
            return (None, None)
        suffix = (path.suffix or "").lower()
        media_type = (
            "image/png"
            if suffix == ".png"
            else "image/webp"
            if suffix == ".webp"
            else "image/jpeg"
        )
        return (path, media_type)

    def get_processing_logs(self, analysis_id: uuid.UUID) -> str | None:
        """Retorna logs de processamento ou None."""
        analysis = self._repository.get_by_id(analysis_id)
        if not analysis:
            return None
        return analysis.processing_logs or ""

    def delete_analysis(self, analysis_id: uuid.UUID) -> None:
        """Remove a análise (e imagem). Levanta 404 se não existir."""
        if not self._repository.delete(analysis_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found",
            )

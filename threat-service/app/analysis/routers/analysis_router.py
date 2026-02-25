"""Analysis router — rotas mínimas, delega para controller."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi_pagination import Page, Params, paginate
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlalchemy.orm import Session

from app.analysis.controllers.analysis_controller import AnalysisController
from app.analysis.schemas import (
    AnalysisCreateResponse,
    AnalysisDetailResponse,
    AnalysisFilter,
    AnalysisListResponse,
)
from app.database import get_db

disable_installed_extensions_check()

router = APIRouter(prefix="/analyses", tags=["Analyses"])


def get_controller(db: Annotated[Session, Depends(get_db)]) -> AnalysisController:
    return AnalysisController(db)


@router.post(
    "",
    response_model=AnalysisCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create analysis",
)
async def create_analysis(
    file: UploadFile = File(..., description="Architecture diagram image"),
    controller: Annotated[AnalysisController, Depends(get_controller)] = None,
):
    """Create new analysis from uploaded image."""
    contents = await file.read()
    return controller.create_analysis(contents, file.filename or "")


@router.get("", response_model=Page[AnalysisListResponse], summary="List analyses")
async def list_analyses(
    params: Params = Depends(),
    filters: AnalysisFilter = Depends(AnalysisFilter),
    controller: Annotated[AnalysisController, Depends(get_controller)] = None,
):
    """
    Lista análises com filtros e paginação.
    Query params: code, status, created_at_from, created_at_to (filtros);
    page, size (paginação via fastapi-pagination).
    """
    items = controller.list_analyses(filters)
    return paginate(items, params)


@router.get(
    "/{analysis_id}",
    response_model=AnalysisDetailResponse,
    summary="Get analysis detail",
)
async def get_analysis(
    analysis_id: uuid.UUID,
    controller: Annotated[AnalysisController, Depends(get_controller)] = None,
):
    """Get analysis by ID including result when ANALISADO."""
    return controller.get_analysis_or_404(analysis_id)


@router.get("/{analysis_id}/image", summary="Get analysis image")
async def get_analysis_image(
    analysis_id: uuid.UUID,
    controller: Annotated[AnalysisController, Depends(get_controller)] = None,
):
    """Serve the uploaded diagram image."""
    path, media_type = controller.get_image_path_and_media_type(analysis_id)
    if path is None or media_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    return FileResponse(path, media_type=media_type)


@router.get("/{analysis_id}/logs", summary="Get processing logs")
async def get_analysis_logs(
    analysis_id: uuid.UUID,
    controller: Annotated[AnalysisController, Depends(get_controller)] = None,
):
    """Get processing logs (JSON)."""
    logs = controller.get_processing_logs(analysis_id)
    if logs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    return {"logs": logs}


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete analysis",
)
async def delete_analysis(
    analysis_id: uuid.UUID,
    controller: Annotated[AnalysisController, Depends(get_controller)] = None,
):
    """Remove a análise (interrompe processamento se em andamento e remove do banco). Ação irreversível."""
    controller.delete_analysis(analysis_id)

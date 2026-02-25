"""Threat Analysis API router - views only, delegates to controller."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import SettingsDep
from app.threat_analysis.controllers import ThreatAnalysisController
from app.threat_analysis.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    get_analysis_request,
)
from app.threat_analysis.service import ThreatModelService, get_threat_model_service

router = APIRouter()

ServiceDep = Annotated[ThreatModelService, Depends(get_threat_model_service)]


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze Architecture Diagram",
    description="Upload an architecture diagram image to receive STRIDE/DREAD threat analysis.",
)
async def analyze_diagram(
    service: ServiceDep,
    settings: SettingsDep,
    request: Annotated[AnalysisRequest, Depends(get_analysis_request)],
) -> AnalysisResponse:
    """Analyze an architecture diagram for security threats."""
    contents = await request.file.read()
    return await ThreatAnalysisController(service, settings).analyze(
        contents,
        content_type=request.file.content_type,
    )

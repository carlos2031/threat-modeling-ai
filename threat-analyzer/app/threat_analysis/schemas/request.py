"""Request schemas for the threat analysis API."""

from typing import Annotated

from fastapi import File, UploadFile
from pydantic import ConfigDict, Field

from .base import BaseSchema


class AnalysisRequest(BaseSchema):
    """Request payload for POST /analyze (diagram threat analysis).

    The client sends an image of an architecture diagram (PNG, JPEG, WebP, or GIF).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: Annotated[
        UploadFile,
        Field(
            description=(
                "Image file of the architecture diagram. Accepted types: image/png, "
                "image/jpeg, image/webp, image/gif. Content is used for diagram extraction "
                "and STRIDE/DREAD threat analysis."
            ),
        ),
    ]


def get_analysis_request(
    file: UploadFile = File(
        ...,
        description=(
            "Architecture diagram image. Accepted: image/png, image/jpeg, image/webp, image/gif."
        ),
    ),
) -> AnalysisRequest:
    """Build AnalysisRequest from multipart file (FastAPI dependency)."""
    return AnalysisRequest(file=file)

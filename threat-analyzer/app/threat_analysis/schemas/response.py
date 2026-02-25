"""API response schemas for the threat analysis endpoint.

The main response (AnalysisResponse) returns the extracted diagram structure,
the list of threats with STRIDE/DREAD, and an aggregate risk score and level.
"""

from enum import Enum

from pydantic import Field, computed_field

from .base import BaseSchema
from .component import Component, Connection
from .threat import Threat


class RiskLevel(str, Enum):
    """Aggregate risk level derived from the overall risk score (0–10).

    Used to quickly communicate severity: LOW (<3), MEDIUM (3–6), HIGH (6–8),
    CRITICAL (8–10). See from_score() for the exact thresholds.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_score(cls, score: float) -> "RiskLevel":
        """Map a numeric risk score (0–10) to a RiskLevel.

        Thresholds: LOW score < 3; MEDIUM score < 6; HIGH score < 8; CRITICAL otherwise.
        """
        if score < 3:
            return cls.LOW
        if score < 6:
            return cls.MEDIUM
        if score < 8:
            return cls.HIGH
        return cls.CRITICAL


class AnalysisResponse(BaseSchema):
    """Full response from POST /analyze: diagram structure, threats, and risk.

    Contains the components and connections extracted from the diagram, the
    list of threats (each with STRIDE category and DREAD scoring), and an
    overall risk_score (0–10) plus risk_level (LOW/MEDIUM/HIGH/CRITICAL).
    threat_count and component_count are computed for convenience.
    """

    model_used: str = Field(
        ...,
        description="Identifier of the model that performed the analysis (e.g. gemini-1.5-pro).",
    )
    components: list[Component] = Field(
        default_factory=list,
        description="Architecture components detected in the diagram.",
    )
    connections: list[Connection] = Field(
        default_factory=list,
        description="Connections (data flows / dependencies) between components.",
    )
    threats: list[Threat] = Field(
        default_factory=list,
        description="Identified threats with STRIDE category, description, mitigation, and DREAD scores.",
    )
    risk_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Overall risk score from 0 (low) to 10 (critical), derived from DREAD.",
    )
    risk_level: RiskLevel = Field(
        ...,
        description="Aggregate risk level (LOW/MEDIUM/HIGH/CRITICAL) from risk_score.",
    )
    processing_time: float | None = Field(
        default=None,
        description="Total analysis processing time in seconds, if measured.",
    )

    @computed_field
    @property
    def threat_count(self) -> int:
        """Number of threats identified in the analysis."""
        return len(self.threats)

    @computed_field
    @property
    def component_count(self) -> int:
        """Number of components detected in the diagram."""
        return len(self.components)

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.config.model_config import RainfallClass, RiskLevel, SusceptibilityClass
from app.schemas.satellite_evidence import CoordinateLocation, EvidenceQualityStatus


class EvidenceFactorType(str, Enum):
    TERRAIN_SUSCEPTIBILITY = "TERRAIN_SUSCEPTIBILITY"
    RAINFALL_TRIGGER = "RAINFALL_TRIGGER"
    SOIL_SATURATION = "SOIL_SATURATION"
    SAR_SURFACE_CHANGE = "SAR_SURFACE_CHANGE"
    OPTICAL_VEGETATION_LOSS = "OPTICAL_VEGETATION_LOSS"
    INFRASTRUCTURE_PROXIMITY = "INFRASTRUCTURE_PROXIMITY"
    FIELD_OBSERVATION = "FIELD_OBSERVATION"


class EvidenceConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    PROVISIONAL = "PROVISIONAL"


class EvidenceFactor(BaseModel):
    factor_id: str
    factor_type: EvidenceFactorType
    source: str
    parameter: str
    observed_value: Any
    baseline_value: Optional[Any] = None
    difference: Optional[Any] = None
    indicator_score: float = Field(..., ge=0.0, le=1.0, description="Normalized risk contribution (0.0 to 1.0)")
    weight: float = Field(..., ge=0.0, le=1.0, description="Configured relative weight in evidence breakdown")
    status: EvidenceQualityStatus = EvidenceQualityStatus.VALID
    quality_notes: Optional[str] = None
    interpretation: str
    is_supporting: bool = True  # True = raises risk/evidence, False = conflicting/dampening
    verification_required: bool = False

    model_config = ConfigDict(from_attributes=True)


class EvidenceSummaryResponse(BaseModel):
    location: CoordinateLocation
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    overall_evidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Heuristic multi-source evidence score (0.0 to 1.0, not calibrated probability)"
    )
    evidence_level: RiskLevel
    confidence: EvidenceConfidence
    data_quality_score: float = Field(..., ge=0.0, le=1.0, description="Fraction of active/valid evidence factors")
    is_provisional: bool = True
    
    # Model Outputs for reference (unmodified)
    model1_susceptibility_probability: Optional[float] = None
    model1_susceptibility_class: Optional[SusceptibilityClass] = None
    model2_dynamic_probability: Optional[float] = None
    model2_warning_candidate: Optional[bool] = None
    rainfall_24h_mm: float = 0.0
    rainfall_class: RainfallClass = RainfallClass.LOW

    # Factor breakdowns
    factors: List[EvidenceFactor] = Field(default_factory=list)
    supporting_factors: List[str] = Field(default_factory=list)
    conflicting_factors: List[str] = Field(default_factory=list)
    missing_factors: List[str] = Field(default_factory=list)
    
    # Operational Guidance
    recommended_action: str
    verification_requirement: str
    provenance_trail: Dict[str, Any] = Field(default_factory=dict)
    scientific_disclaimer: str = (
        "Multi-source evidence fusion is a transparent heuristic indicator for decision support. "
        "It does NOT replace calibrated disaster early warnings and does not alter the underlying trained ML model weights."
    )


class EvidenceEvaluationRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    include_satellite_check: bool = True
    include_exposure_check: bool = True

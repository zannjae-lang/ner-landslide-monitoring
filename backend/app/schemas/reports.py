from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.config.model_config import RiskLevel, SusceptibilityClass
from app.schemas.satellite_evidence import CoordinateLocation


class ContributionDirection(str, Enum):
    INCREASES_RISK = "INCREASES_RISK"
    DECREASES_RISK = "DECREASES_RISK"
    NEUTRAL = "NEUTRAL"


class FeatureAttribution(BaseModel):
    feature_name: str
    feature_display_name: str
    observed_value: Any
    unit: str
    direction: ContributionDirection
    relative_importance_score: float = Field(..., ge=0.0, le=1.0)
    plain_language_impact: str

    model_config = ConfigDict(from_attributes=True)


class ModelExplainabilityBreakdown(BaseModel):
    model_name: str
    model_version: str
    prediction_probability: float
    classification_label: str
    decision_threshold: float
    threshold_exceeded: bool
    top_contributing_features: List[FeatureAttribution] = Field(default_factory=list)
    methodology_note: str = (
        "Feature attributions computed from tree path splits and normalized baseline deviations. "
        "Represents local explainability approximation for disaster decision support."
    )


class ExplainableRiskReport(BaseModel):
    report_id: str
    location: CoordinateLocation
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    final_risk_level: RiskLevel
    combined_risk_score: float
    data_freshness_status: str
    
    # Model explanations
    model1_susceptibility_explainability: ModelExplainabilityBreakdown
    model2_dynamic_explainability: ModelExplainabilityBreakdown
    
    # Evidence & Exposure briefs
    meteorological_summary: str
    satellite_evidence_summary: str
    exposure_summary: str
    
    # High-level Brief for District Disaster Management Authority (DDMA)
    executive_summary_narrative: str
    key_risk_drivers: List[str] = Field(default_factory=list)
    recommended_sop_actions: List[str] = Field(default_factory=list)
    verification_requirements: str
    
    disclaimer: str = (
        "PROTOTYPE RESEARCH OUTPUT: This report provides AI/Remote Sensing explainability and decision support. "
        "It is not an official government disaster declaration."
    )

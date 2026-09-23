from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.config.model_config import RiskLevel, SusceptibilityClass


class GridCell(BaseModel):
    cell_id: str
    latitude: float
    longitude: float
    state: str
    district: str
    elevation_m: float
    slope_deg: float
    susceptibility_probability: float
    susceptibility_class: SusceptibilityClass
    dynamic_probability: float
    combined_risk_score: float
    risk_level: RiskLevel
    rainfall_24h_mm: float
    is_hotspot: bool = False
    data_status: str = "Fresh"

    model_config = ConfigDict(from_attributes=True)


class GridHotspotResponse(BaseModel):
    total_cells: int
    high_threat_cells: int
    resolution_degrees: float = 0.05
    bounding_box: Dict[str, float]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cells: List[GridCell]
    state_breakdown: Dict[str, int] = Field(default_factory=dict)
    disclaimer: str = (
        "Regional grid cells represent spatial sampling approximations (~5.5km resolution) "
        "and do not capture localized micro-slope failures below 30m."
    )


class StateRiskSummary(BaseModel):
    state_name: str
    monitored_stations: int
    high_threat_stations: int
    max_risk_score: float
    mean_risk_score: float
    dominant_risk_level: RiskLevel
    max_rainfall_24h_mm: float
    primary_vulnerabilities: List[str] = Field(default_factory=list)


class StateSummaryResponse(BaseModel):
    total_states: int = 8
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    states: List[StateRiskSummary]


class DistrictRankingItem(BaseModel):
    district: str
    state: str
    composite_vulnerability_score: float = Field(..., ge=0.0, le=1.0)
    high_risk_zone_area_pct: float
    avg_slope_deg: float
    recent_rainfall_24h_mm: float
    monitored_points: int


class DistrictRankingResponse(BaseModel):
    total_districts: int
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rankings: List[DistrictRankingItem]

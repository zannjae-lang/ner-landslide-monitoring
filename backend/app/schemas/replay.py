from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.config.model_config import RiskLevel, SusceptibilityClass


class HistoricalLandslideEvent(BaseModel):
    event_id: str
    event_name: str
    location_name: str
    state: str
    district: str
    event_date: str
    latitude: float
    longitude: float
    elevation_m: float
    slope_deg: float
    triggering_rainfall_24h_mm: float
    antecedent_rainfall_7day_mm: float
    reported_impact: str
    geological_setting: str
    historical_satellite_status: str

    model_config = ConfigDict(from_attributes=True)


class TimelineStep(BaseModel):
    day_offset: int
    date_str: str
    rainfall_24h_mm: float
    cumulative_rainfall_mm: float
    simulated_dynamic_prob: float
    simulated_risk_score: float
    simulated_risk_level: RiskLevel
    alert_triggered: bool


class EventReplaySimulationResponse(BaseModel):
    event_details: HistoricalLandslideEvent
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    static_susceptibility_probability: float
    static_susceptibility_class: SusceptibilityClass
    peak_dynamic_probability: float
    peak_combined_risk_score: float
    peak_risk_level: RiskLevel
    lead_time_hours_to_warning: float
    timeline: List[TimelineStep] = Field(default_factory=list)
    retrospective_validation_notes: str
    scientific_caveat: str = (
        "Demonstration scenario based on published IMD/GSI rainfall reanalysis data. "
        "Historical replay demonstrates model sensitivity and does not imply real-time operational certification."
    )


class HistoricalEventsListResponse(BaseModel):
    total_events: int
    events: List[HistoricalLandslideEvent]

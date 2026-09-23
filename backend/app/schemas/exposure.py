from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.config.model_config import RiskLevel
from app.schemas.satellite_evidence import CoordinateLocation


class AssetType(str, Enum):
    HIGHWAY = "HIGHWAY"
    STATE_ROAD = "STATE_ROAD"
    BRIDGE = "BRIDGE"
    RAILWAY = "RAILWAY"
    SETTLEMENT = "SETTLEMENT"
    HOSPITAL = "HOSPITAL"
    SCHOOL = "SCHOOL"
    COMMUNICATION_TOWER = "COMMUNICATION_TOWER"


class ExposedAsset(BaseModel):
    asset_id: str
    asset_type: AssetType
    name: str
    distance_meters: float
    within_analysis_buffer: bool = True
    estimated_population_impact: Optional[int] = None
    risk_level_at_asset: RiskLevel = RiskLevel.WATCH
    coordinates: List[float] = Field(..., description="[longitude, latitude]")

    model_config = ConfigDict(from_attributes=True)


class ExposureAnalysisRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    buffer_radius_meters: float = Field(1000.0, ge=100.0, le=5000.0)


class ExposureAnalysisResponse(BaseModel):
    location: CoordinateLocation
    analysis_buffer_meters: float
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_exposed_assets: int
    critical_infrastructure_count: int
    exposure_risk_rating: str = Field(..., description="Low, Moderate, High, Severe Exposure")
    exposed_assets: List[ExposedAsset] = Field(default_factory=list)
    completeness_warning: str = (
        "Infrastructure and road vector data derived from OpenStreetMap & regional GIS layers. "
        "Vector coverage in remote hill tracts may be incomplete and requires field survey validation."
    )


class RouteSegmentRisk(BaseModel):
    segment_index: int
    start_coordinates: List[float] = Field(..., description="[lon, lat]")
    end_coordinates: List[float] = Field(..., description="[lon, lat]")
    length_km: float
    elevation_m: float
    slope_deg: float
    segment_risk_score: float
    segment_risk_level: RiskLevel
    rainfall_24h_mm: float
    nearby_hotspots_count: int = 0
    chokepoint_warning: Optional[str] = None


class CorridorRiskRequest(BaseModel):
    corridor_id: Optional[str] = None
    corridor_name: Optional[str] = None
    polyline_coordinates: Optional[List[List[float]]] = Field(
        None, description="Optional custom route [[lon, lat], [lon, lat], ...]"
    )
    buffer_distance_meters: float = Field(500.0, ge=100.0, le=3000.0)


class CorridorRiskResponse(BaseModel):
    corridor_id: str
    corridor_name: str
    state_corridor: str
    total_length_km: float
    total_segments: int
    high_risk_segments_count: int
    max_segment_risk: float
    average_segment_risk: float
    critical_chokepoints: List[str] = Field(default_factory=list)
    segments: List[RouteSegmentRisk] = Field(default_factory=list)
    recommended_action: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    caveat: str = (
        "Route corridor risk indicates cumulative slope and precipitation vulnerability along sampled segments. "
        "It does NOT confirm active road blockage without verified traffic police or NHIDCL ground dispatch."
    )

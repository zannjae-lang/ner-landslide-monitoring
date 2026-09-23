from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.config.model_config import DataQualityStatus


class RainfallWindows(BaseModel):
    rainfall_1h: float = Field(..., ge=0.0, description="1h mm")
    rainfall_3h: float = Field(..., ge=0.0, description="3h mm")
    rainfall_6h: float = Field(..., ge=0.0, description="6h mm")
    rainfall_12h: float = Field(..., ge=0.0, description="12h mm")
    rainfall_24h: float = Field(..., ge=0.0, description="24h mm")
    rainfall_3day: float = Field(..., ge=0.0, description="3d mm")
    rainfall_7day: float = Field(..., ge=0.0, description="7d mm")


class SoilMoistureLayers(BaseModel):
    layer1_surface: float = Field(..., description="0-7 cm volumetric m3/m3")
    layer2_rootzone: float = Field(..., description="7-28 cm volumetric m3/m3")


class WeatherObservationResponse(BaseModel):
    location_id: Optional[str] = None
    latitude: float
    longitude: float
    provider: str
    observed_at: datetime
    retrieved_at: datetime
    data_age_hours: float
    quality_status: DataQualityStatus
    rainfall_windows: RainfallWindows
    soil_moisture: SoilMoistureLayers
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None

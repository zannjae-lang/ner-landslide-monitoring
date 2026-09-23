from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.model_config import DataQualityStatus
from app.db.session import get_db
from app.repositories.location_repository import LocationRepository
from app.repositories.observation_repository import ObservationRepository
from app.schemas.weather import RainfallWindows, SoilMoistureLayers, WeatherObservationResponse
from app.services.data_collectors.collector_manager import collector_manager

router = APIRouter(prefix="/weather", tags=["Weather & Telemetry"])


@router.get("/{location_id}", response_model=WeatherObservationResponse)
async def get_location_weather(location_id: str, db: Session = Depends(get_db)):
    """Fetch latest weather observations and multi-layer soil moisture for a station."""
    loc_repo = LocationRepository(db)
    loc = loc_repo.get_by_id(location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    obs = await collector_manager.get_observation(loc.latitude, loc.longitude)
    now = datetime.now(timezone.utc)
    age_hours = round((now - obs.observed_at).total_seconds() / 3600.0, 2)

    return WeatherObservationResponse(
        location_id=loc.id,
        latitude=loc.latitude,
        longitude=loc.longitude,
        provider=obs.provider_id,
        observed_at=obs.observed_at,
        retrieved_at=obs.retrieved_at,
        data_age_hours=age_hours,
        quality_status=DataQualityStatus.FRESH if age_hours <= 6 else DataQualityStatus.STALE,
        rainfall_windows=RainfallWindows(
            rainfall_1h=obs.rainfall_1h_mm,
            rainfall_3h=obs.rainfall_3h_mm,
            rainfall_6h=obs.rainfall_6h_mm,
            rainfall_12h=obs.rainfall_12h_mm,
            rainfall_24h=obs.rainfall_24h_mm,
            rainfall_3day=obs.rainfall_3day_mm,
            rainfall_7day=obs.rainfall_7day_mm,
        ),
        soil_moisture=SoilMoistureLayers(
            layer1_surface=obs.soil_moisture_layer_1,
            layer2_rootzone=obs.soil_moisture_layer_2,
        ),
        temperature_c=obs.temperature_c,
        humidity_percent=obs.humidity_percent,
    )

import asyncio
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.location import Location
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.predictions import PredictionRunRequest
from app.services.ml_models.prediction_pipeline import prediction_pipeline

router = APIRouter(prefix="/map", tags=["GIS & Map Intelligence"])


@router.get("/risk")
async def get_map_risk_layer(
    state: Optional[str] = Query(None),
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lon: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return compact GeoJSON FeatureCollection optimized for Leaflet map layers across NER states."""
    query = db.query(Location)
    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))
    if min_lat is not None and max_lat is not None:
        query = query.filter(Location.latitude.between(min_lat, max_lat))
    if min_lon is not None and max_lon is not None:
        query = query.filter(Location.longitude.between(min_lon, max_lon))

    locations = query.all()
    pred_repo = PredictionRepository(db)
    
    sem = asyncio.Semaphore(10)

    async def get_feature_for_loc(loc: Location) -> Dict[str, Any]:
        async with sem:
            latest = pred_repo.get_latest_by_location(loc.id)
            if latest and latest.details_json:
                p_data = latest.details_json
            else:
                req = PredictionRunRequest(
                    location_id=loc.id,
                    location_name=loc.name,
                    state=loc.state,
                    district=loc.district,
                    latitude=loc.latitude,
                    longitude=loc.longitude,
                )
                res = await prediction_pipeline.execute_prediction(req, db=db, persist=True)
                p_data = res.model_dump(mode="json")

            return {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [loc.longitude, loc.latitude],
                },
                "properties": {
                    "location_id": loc.id,
                    "name": loc.name,
                    "state": loc.state,
                    "district": loc.district,
                    "elevation_m": loc.elevation_m,
                    "slope_deg": loc.slope_deg,
                    "final_risk": p_data.get("final_risk", "Normal"),
                    "combined_risk_score": p_data.get("combined_risk_score", 0.0),
                    "susceptibility_probability": p_data.get("model1_result", {}).get("susceptibility_probability", 0.0) if p_data.get("model1_result") else 0.0,
                    "susceptibility_class": p_data.get("model1_result", {}).get("susceptibility_class", "Very Low") if p_data.get("model1_result") else "Very Low",
                    "dynamic_probability": p_data.get("model2_result", {}).get("dynamic_probability", 0.0) if p_data.get("model2_result") else 0.0,
                    "warning_candidate": p_data.get("model2_result", {}).get("warning_candidate", False) if p_data.get("model2_result") else False,
                    "rainfall_24h_mm": p_data.get("rainfall_24h_mm", 0.0),
                    "rainfall_class": p_data.get("rainfall_class", "Low"),
                    "data_status": p_data.get("data_status", "Fresh"),
                    "data_age_hours": p_data.get("data_age_hours", 0.0),
                    "is_stale": p_data.get("is_stale", False),
                    "prototype_status": "Uncalibrated Prototype",
                },
            }

    features = await asyncio.gather(*[get_feature_for_loc(loc) for loc in locations])

    return {
        "type": "FeatureCollection",
        "total": len(features),
        "features": list(features),
    }

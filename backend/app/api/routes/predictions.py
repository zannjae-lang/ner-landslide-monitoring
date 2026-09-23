from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.location_repository import LocationRepository
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.predictions import PredictionRunRequest, RiskEngineResult
from app.services.ml_models.prediction_pipeline import prediction_pipeline

router = APIRouter(prefix="/predictions", tags=["Predictions & Risk Inference"])


@router.post("/run", response_model=RiskEngineResult)
async def run_prediction(
    request: PredictionRunRequest,
    db: Session = Depends(get_db),
):
    """Execute end-to-end multi-factor prediction pipeline (Model 1 -> Model 2 -> Risk Engine 2.0)."""
    try:
        result = await prediction_pipeline.execute_prediction(request, db=db, persist=True)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction pipeline failure: {str(e)}")


@router.get("/latest/{location_id}", response_model=RiskEngineResult)
async def get_latest_prediction(location_id: str, db: Session = Depends(get_db)):
    """Retrieve latest cached prediction or execute a real-time run for the station."""
    loc_repo = LocationRepository(db)
    loc = loc_repo.get_by_id(location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    pred_repo = PredictionRepository(db)
    latest = pred_repo.get_latest_by_location(location_id)
    
    if latest and latest.details_json:
        return RiskEngineResult(**latest.details_json)

    # If no prediction cached yet, execute live run
    req = PredictionRunRequest(
        location_id=loc.id,
        location_name=loc.name,
        state=loc.state,
        district=loc.district,
        latitude=loc.latitude,
        longitude=loc.longitude,
    )
    return await prediction_pipeline.execute_prediction(req, db=db, persist=True)


@router.get("/history")
def get_prediction_history(
    location_id: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve historical prediction audit logs with filtering."""
    repo = PredictionRepository(db)
    total, items = repo.list_predictions(
        location_id=location_id,
        state=state,
        district=district,
        risk_level=risk_level,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit,
    )
    
    history_items = []
    for item in items:
        loc = item.location
        history_items.append({
            "id": item.id,
            "location_id": item.location_id,
            "location_name": loc.name if loc else "Unknown",
            "state": loc.state if loc else "Unknown",
            "district": loc.district if loc else "Unknown",
            "prediction_timestamp": item.prediction_timestamp,
            "model1_probability": item.model1_probability,
            "model1_class": item.model1_class,
            "model2_probability": item.model2_probability,
            "warning_candidate": item.warning_candidate,
            "rainfall_24h_mm": item.rainfall_24h_mm,
            "rainfall_class": item.rainfall_class,
            "combined_risk_score": item.combined_risk_score,
            "final_risk": item.final_risk,
            "data_status": item.data_status,
            "data_age_hours": item.data_age_hours,
            "is_stale": item.is_stale,
            "prototype_flag": item.prototype_flag,
        })

    return {"total": total, "items": history_items}

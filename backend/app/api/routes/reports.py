from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.location_repository import LocationRepository
from app.schemas.reports import ExplainableRiskReport
from app.services.reporting.explainability_service import explainability_service

router = APIRouter(prefix="/reports", tags=["Explainable AI & Risk Reports"])


class ReportGenerateRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


@router.post("/generate", response_model=ExplainableRiskReport)
async def generate_explainable_report(request: ReportGenerateRequest):
    """Generate structured Explainable AI risk report with factor attributions and DDMA response protocol."""
    try:
        return await explainability_service.generate_report(
            latitude=request.latitude,
            longitude=request.longitude,
            location_id=request.location_id,
            location_name=request.location_name,
            state=request.state,
            district=request.district,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}",
        )


@router.get("/explain/location/{location_id}", response_model=ExplainableRiskReport)
async def get_station_explainable_report(location_id: str, db: Session = Depends(get_db)):
    """Generate on-demand explainable assessment breakdown for a registered monitoring station."""
    loc_repo = LocationRepository(db)
    loc = loc_repo.get_by_id(location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Monitoring station not found")

    return await explainability_service.generate_report(
        latitude=loc.latitude,
        longitude=loc.longitude,
        location_id=loc.id,
        location_name=loc.name,
        state=loc.state,
        district=loc.district,
    )

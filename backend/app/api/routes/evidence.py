from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.location_repository import LocationRepository
from app.schemas.evidence import EvidenceEvaluationRequest, EvidenceSummaryResponse
from app.services.evidence.evidence_service import evidence_service

router = APIRouter(prefix="/evidence", tags=["Evidence & Multi-Source Fusion"])


@router.post("/evaluate", response_model=EvidenceSummaryResponse)
async def evaluate_coordinates_evidence(request: EvidenceEvaluationRequest):
    """Evaluate multi-source disaster intelligence evidence across terrain, meteorology, and remote sensing."""
    try:
        return await evidence_service.evaluate_evidence(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evidence evaluation failed: {str(e)}",
        )


@router.get("/location/{location_id}", response_model=EvidenceSummaryResponse)
async def evaluate_station_evidence(
    location_id: str,
    include_satellite: bool = True,
    db: Session = Depends(get_db),
):
    """Evaluate comprehensive multi-source evidence breakdown for a registered monitoring station."""
    loc_repo = LocationRepository(db)
    loc = loc_repo.get_by_id(location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    req = EvidenceEvaluationRequest(
        location_id=loc.id,
        location_name=loc.name,
        state=loc.state,
        district=loc.district,
        latitude=loc.latitude,
        longitude=loc.longitude,
        include_satellite_check=include_satellite,
    )
    return await evidence_service.evaluate_evidence(req)

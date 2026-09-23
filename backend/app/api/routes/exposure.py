from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from app.schemas.exposure import (
    CorridorRiskRequest,
    CorridorRiskResponse,
    ExposureAnalysisRequest,
    ExposureAnalysisResponse,
)
from app.services.exposure.exposure_service import exposure_service
from app.services.exposure.route_risk_service import route_risk_service

router = APIRouter(prefix="/exposure", tags=["Infrastructure Exposure & Corridor Risk"])


@router.post("/analyze", response_model=ExposureAnalysisResponse)
async def analyze_location_exposure(request: ExposureAnalysisRequest):
    """Evaluate physical assets, roads, bridges, settlements, and schools within landslide hazard buffer."""
    try:
        return await exposure_service.analyze_exposure(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Infrastructure exposure analysis failed: {str(e)}",
        )


@router.get("/corridors", response_model=List[Dict[str, Any]])
def list_critical_transport_corridors():
    """List predefined high-priority transport lifelines across the 8 NER states."""
    return route_risk_service.list_available_corridors()


@router.post("/corridor-risk", response_model=CorridorRiskResponse)
async def evaluate_corridor_risk(request: CorridorRiskRequest):
    """Evaluate segmental landslide risk, slope hazards, and chokepoints along an arterial highway corridor."""
    try:
        return await route_risk_service.evaluate_corridor_risk(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Corridor risk evaluation failed: {str(e)}",
        )

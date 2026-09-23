from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.grid import DistrictRankingResponse, GridHotspotResponse, StateSummaryResponse
from app.services.spatial.grid_service import grid_service

router = APIRouter(prefix="/spatial", tags=["NER Spatial & Regional Hotspots"])


@router.get("/hotspots", response_model=GridHotspotResponse)
async def get_regional_hotspots(
    state: Optional[str] = Query(None, description="Filter by NER State (e.g. Sikkim, Assam, Mizoram)"),
    min_lat: Optional[float] = Query(None, ge=-90.0, le=90.0),
    max_lat: Optional[float] = Query(None, ge=-90.0, le=90.0),
    min_lon: Optional[float] = Query(None, ge=-180.0, le=180.0),
    max_lon: Optional[float] = Query(None, ge=-180.0, le=180.0),
):
    """Retrieve spatial grid sampling and high-threat landslide hotspot cells across the 8 NER states."""
    try:
        return await grid_service.compute_spatial_hotspots(
            state_filter=state,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Regional hotspot spatial query failed: {str(e)}",
        )


@router.get("/states/summary", response_model=StateSummaryResponse)
async def get_states_risk_summary():
    """Retrieve macro-level risk and vulnerability summaries across all eight North Eastern states."""
    try:
        return await grid_service.compute_states_summary()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"State risk summaries query failed: {str(e)}",
        )


@router.get("/district-rankings", response_model=DistrictRankingResponse)
async def get_district_vulnerability_rankings():
    """Retrieve objective multi-factor district vulnerability rankings across terrain and rainfall factors."""
    try:
        return await grid_service.compute_district_rankings()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"District rankings query failed: {str(e)}",
        )

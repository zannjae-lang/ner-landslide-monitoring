from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.satellite_evidence import (
    SatelliteMetadataResponse,
    Sentinel1ChangeResponse,
    Sentinel2NDVIResponse,
)
from app.services.satellite.s1_change_service import s1_change_service
from app.services.satellite.s2_disturbance_service import s2_disturbance_service
from app.services.satellite.satellite_metadata_service import satellite_metadata_service

router = APIRouter(prefix="/satellite-analysis", tags=["Satellite Evidence & Analysis"])


@router.get("/metadata", response_model=SatelliteMetadataResponse)
async def get_satellite_observation_metadata(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Target Latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Target Longitude"),
    location_name: Optional[str] = Query(None, description="Optional monitoring station name"),
    state: Optional[str] = Query(None, description="NER State name"),
    district: Optional[str] = Query(None, description="District name"),
):
    """Retrieve verified observation metadata from Copernicus DEM, Sentinel-1 SAR, and Sentinel-2 Optical."""
    try:
        return await satellite_metadata_service.get_all_satellite_metadata(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            state=state,
            district=district,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Satellite metadata query encountered an unexpected error: {str(e)}",
        )


@router.get("/sentinel1/change", response_model=Sentinel1ChangeResponse)
async def get_sentinel1_surface_change(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Target Latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Target Longitude"),
    location_name: Optional[str] = Query(None, description="Optional monitoring station name"),
    state: Optional[str] = Query(None, description="NER State name"),
    district: Optional[str] = Query(None, description="District name"),
    baseline_lookback_days: int = Query(60, ge=15, le=365, description="Days in past to find matching baseline orbit"),
    recent_lookback_days: int = Query(15, ge=1, le=60, description="Days in past to find latest recent orbit"),
    force_refresh: bool = Query(False, description="Bypass in-memory cache"),
):
    """Evaluate Sentinel-1 SAR Ground Range Detected (GRD) backscatter variation for preliminary surface change evidence."""
    if recent_lookback_days >= baseline_lookback_days:
        raise HTTPException(
            status_code=400,
            detail="recent_lookback_days must be strictly less than baseline_lookback_days.",
        )

    try:
        return await s1_change_service.compute_s1_change(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            state=state,
            district=district,
            baseline_lookback_days=baseline_lookback_days,
            recent_lookback_days=recent_lookback_days,
            force_refresh=force_refresh,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sentinel-1 change detection query encountered an error: {str(e)}",
        )


@router.get("/sentinel2/ndvi", response_model=Sentinel2NDVIResponse)
async def get_sentinel2_vegetation_disturbance(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Target Latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Target Longitude"),
    location_name: Optional[str] = Query(None, description="Optional monitoring station name"),
    state: Optional[str] = Query(None, description="NER State name"),
    district: Optional[str] = Query(None, description="District name"),
    baseline_lookback_days: int = Query(180, ge=30, le=730, description="Baseline observation window in days"),
    recent_lookback_days: int = Query(30, ge=5, le=90, description="Recent observation window in days"),
    max_cloud_percent: float = Query(30.0, ge=0.0, le=100.0, description="Maximum scene cloud cover filter %"),
    force_refresh: bool = Query(False, description="Bypass in-memory cache"),
):
    """Evaluate Sentinel-2 MSI Surface Reflectance NDVI difference for preliminary vegetation disturbance evidence."""
    if recent_lookback_days >= baseline_lookback_days:
        raise HTTPException(
            status_code=400,
            detail="recent_lookback_days must be strictly less than baseline_lookback_days.",
        )

    try:
        return await s2_disturbance_service.compute_s2_disturbance(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            state=state,
            district=district,
            baseline_lookback_days=baseline_lookback_days,
            recent_lookback_days=recent_lookback_days,
            max_cloud_percent=max_cloud_percent,
            force_refresh=force_refresh,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sentinel-2 vegetation disturbance query encountered an error: {str(e)}",
        )

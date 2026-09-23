import asyncio
from typing import Any, Dict, Optional
from fastapi import APIRouter, Query
from app.services.data_collectors.google_earth_engine import gee_service

router = APIRouter(prefix="/satellite", tags=["Satellite Telemetry (GEE)"])


@router.get("/dem")
async def get_satellite_dem(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
) -> Dict[str, Any]:
    """Retrieve 30m Copernicus DEM GLO-30 elevation from Google Earth Engine."""
    return await gee_service.get_dem_elevation(latitude, longitude)


@router.get("/sentinel2")
async def get_sentinel2_ndvi(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    max_cloud_percent: float = Query(30.0, ge=0.0, le=100.0),
) -> Dict[str, Any]:
    """Retrieve Sentinel-2 Optical surface reflectance & NDVI statistics from Google Earth Engine."""
    return await gee_service.get_sentinel2_ndvi(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
        max_cloud_percent=max_cloud_percent,
    )


@router.get("/sentinel1")
async def get_sentinel1_sar(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
) -> Dict[str, Any]:
    """Retrieve Sentinel-1 SAR Ground Range Detected (GRD) backscatter & polarisation from Google Earth Engine."""
    return await gee_service.get_sentinel1_sar(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/summary")
async def get_satellite_summary(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
) -> Dict[str, Any]:
    """Retrieve combined live satellite telemetry snapshot concurrently."""
    dem_task = gee_service.get_dem_elevation(latitude, longitude)
    s2_task = gee_service.get_sentinel2_ndvi(latitude, longitude)
    s1_task = gee_service.get_sentinel1_sar(latitude, longitude)

    dem_res, s2_res, s1_res = await asyncio.gather(dem_task, s2_task, s1_task)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "provider": "google_earth_engine",
        "copernicus_dem": dem_res,
        "sentinel2_optical": s2_res,
        "sentinel1_sar": s1_res,
    }

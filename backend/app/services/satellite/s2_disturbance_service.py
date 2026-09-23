import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.core.logger import logger
from app.schemas.satellite_evidence import (
    CoordinateLocation,
    EvidenceQualityStatus,
    Sentinel2CompositeDetail,
    Sentinel2NDVIResponse,
)
from app.services.data_collectors.google_earth_engine import gee_service
from app.services.quality.satellite_quality_service import satellite_quality_service


class Sentinel2DisturbanceService:
    """Evaluates multi-temporal Sentinel-2 MSI Surface Reflectance NDVI disturbance for vegetation loss evidence."""

    def __init__(self, cache_ttl_seconds: int = 1800):
        # Bounded cache with TTL: cache_key -> (timestamp, response)
        self._cache: Dict[str, Tuple[float, Sentinel2NDVIResponse]] = {}
        self._cache_ttl = cache_ttl_seconds

    def _get_cache_key(
        self,
        lat: float,
        lon: float,
        baseline_days: int,
        recent_days: int,
        max_cloud: float,
    ) -> str:
        return f"{round(lat, 4)}_{round(lon, 4)}_{baseline_days}_{recent_days}_{round(max_cloud, 1)}"

    async def compute_s2_disturbance(
        self,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        baseline_lookback_days: int = 180,
        recent_lookback_days: int = 30,
        max_cloud_percent: float = 30.0,
        force_refresh: bool = False,
    ) -> Sentinel2NDVIResponse:
        location = CoordinateLocation(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            state=state,
            district=district,
        )

        cache_key = self._get_cache_key(
            latitude, longitude, baseline_lookback_days, recent_lookback_days, max_cloud_percent
        )
        if not force_refresh and cache_key in self._cache:
            ts, cached_res = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                return cached_res

        if not gee_service.is_initialized:
            gee_service.initialize()

        if not gee_service.is_initialized:
            return Sentinel2NDVIResponse(
                location=location,
                cloud_threshold_percentage=max_cloud_percent,
                is_valid_comparison=False,
                quality_status=EvidenceQualityStatus.PROVIDER_ERROR,
                missing_data_reasons=["Google Earth Engine authentication credentials not initialized or unavailable."],
            )

        now_utc = datetime.now(timezone.utc)
        recent_start = now_utc - timedelta(days=recent_lookback_days)
        baseline_start = now_utc - timedelta(days=baseline_lookback_days)
        baseline_end = recent_start

        def _fetch_s2_disturbance():
            import ee
            point = ee.Geometry.Point([longitude, latitude])

            def add_ndvi(img):
                return img.addBands(img.normalizedDifference(["B8", "B4"]).rename("NDVI"))

            # Recent Collection
            recent_coll = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(point)
                .filterDate(recent_start.strftime("%Y-%m-%d"), now_utc.strftime("%Y-%m-%d"))
                .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", max_cloud_percent))
                .map(add_ndvi)
            )

            recent_count = recent_coll.size().getInfo()

            # Baseline Collection
            baseline_coll = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(point)
                .filterDate(baseline_start.strftime("%Y-%m-%d"), baseline_end.strftime("%Y-%m-%d"))
                .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", max_cloud_percent))
                .map(add_ndvi)
            )

            baseline_count = baseline_coll.size().getInfo()

            if recent_count == 0 or baseline_count == 0:
                return {
                    "status": "INSUFFICIENT_DATA",
                    "recent_count": recent_count,
                    "baseline_count": baseline_count,
                    "recent": None,
                    "baseline": None,
                }

            # Sample Recent Composite
            recent_median = recent_coll.select("NDVI").median()
            recent_ndvi = (
                recent_median.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=100000)
                .getInfo()
                .get("NDVI")
            )
            recent_cloud = (
                recent_coll.reduceColumns(ee.Reducer.mean(), ["CLOUDY_PIXEL_PERCENTAGE"]).getInfo().get("mean")
            )
            recent_latest = ee.Image(recent_coll.sort("system:time_start", False).first())
            recent_latest_ms = recent_latest.get("system:time_start").getInfo()
            recent_latest_date = (
                datetime.fromtimestamp(recent_latest_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
                if recent_latest_ms
                else None
            )

            # Sample Baseline Composite
            baseline_median = baseline_coll.select("NDVI").median()
            baseline_ndvi = (
                baseline_median.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=100000)
                .getInfo()
                .get("NDVI")
            )
            baseline_cloud = (
                baseline_coll.reduceColumns(ee.Reducer.mean(), ["CLOUDY_PIXEL_PERCENTAGE"]).getInfo().get("mean")
            )
            baseline_latest = ee.Image(baseline_coll.sort("system:time_start", False).first())
            baseline_latest_ms = baseline_latest.get("system:time_start").getInfo()
            baseline_latest_date = (
                datetime.fromtimestamp(baseline_latest_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
                if baseline_latest_ms
                else None
            )

            return {
                "status": "SUCCESS",
                "recent_count": recent_count,
                "baseline_count": baseline_count,
                "recent": {
                    "count": recent_count,
                    "ndvi": round(float(recent_ndvi), 3) if recent_ndvi is not None else None,
                    "cloud": round(float(recent_cloud), 1) if recent_cloud is not None else 0.0,
                    "latest_date": recent_latest_date,
                    "start": recent_start.strftime("%Y-%m-%d"),
                    "end": now_utc.strftime("%Y-%m-%d"),
                },
                "baseline": {
                    "count": baseline_count,
                    "ndvi": round(float(baseline_ndvi), 3) if baseline_ndvi is not None else None,
                    "cloud": round(float(baseline_cloud), 1) if baseline_cloud is not None else 0.0,
                    "latest_date": baseline_latest_date,
                    "start": baseline_start.strftime("%Y-%m-%d"),
                    "end": baseline_end.strftime("%Y-%m-%d"),
                },
            }

        try:
            raw = await asyncio.to_thread(_fetch_s2_disturbance)
        except Exception as e:
            logger.warning(f"GEE S2 disturbance query failed for ({latitude}, {longitude}): {e}")
            return Sentinel2NDVIResponse(
                location=location,
                cloud_threshold_percentage=max_cloud_percent,
                is_valid_comparison=False,
                quality_status=EvidenceQualityStatus.PROVIDER_ERROR,
                missing_data_reasons=[f"Earth Engine query execution failed: {str(e)}"],
            )

        recent_count = raw.get("recent_count", 0)
        baseline_count = raw.get("baseline_count", 0)

        if raw["status"] != "SUCCESS":
            quality_status, is_valid, reasons = satellite_quality_service.evaluate_sentinel2_quality(
                baseline_count=baseline_count,
                recent_count=recent_count,
                baseline_cloud=0.0,
                recent_cloud=0.0,
                cloud_threshold=max_cloud_percent,
                baseline_ndvi=None,
                recent_ndvi=None,
            )
            return Sentinel2NDVIResponse(
                location=location,
                cloud_threshold_percentage=max_cloud_percent,
                is_valid_comparison=False,
                quality_status=quality_status,
                missing_data_reasons=reasons,
            )

        rec_data = raw["recent"]
        base_data = raw["baseline"]

        recent_comp = Sentinel2CompositeDetail(
            period_start=rec_data["start"],
            period_end=rec_data["end"],
            image_count=rec_data["count"],
            mean_cloud_percentage=rec_data["cloud"],
            ndvi_mean=rec_data["ndvi"],
            ndvi_p50=rec_data["ndvi"],
            latest_acquisition_date=rec_data["latest_date"],
        )

        baseline_comp = Sentinel2CompositeDetail(
            period_start=base_data["start"],
            period_end=base_data["end"],
            image_count=base_data["count"],
            mean_cloud_percentage=base_data["cloud"],
            ndvi_mean=base_data["ndvi"],
            ndvi_p50=base_data["ndvi"],
            latest_acquisition_date=base_data["latest_date"],
        )

        quality_status, is_valid, reasons = satellite_quality_service.evaluate_sentinel2_quality(
            baseline_count=baseline_count,
            recent_count=recent_count,
            baseline_cloud=base_data["cloud"],
            recent_cloud=rec_data["cloud"],
            cloud_threshold=max_cloud_percent,
            baseline_ndvi=base_data["ndvi"],
            recent_ndvi=rec_data["ndvi"],
        )

        delta_ndvi = None
        if rec_data.get("ndvi") is not None and base_data.get("ndvi") is not None:
            delta_ndvi = round(rec_data["ndvi"] - base_data["ndvi"], 3)

        response = Sentinel2NDVIResponse(
            location=location,
            cloud_threshold_percentage=max_cloud_percent,
            baseline_composite=baseline_comp,
            recent_composite=recent_comp,
            delta_ndvi=delta_ndvi,
            is_valid_comparison=is_valid,
            quality_status=quality_status,
            missing_data_reasons=reasons,
        )

        self._cache[cache_key] = (time.time(), response)
        if len(self._cache) > 100:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            self._cache.pop(oldest_key, None)

        return response


s2_disturbance_service = Sentinel2DisturbanceService()

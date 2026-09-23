import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.core.logger import logger
from app.schemas.satellite_evidence import (
    CoordinateLocation,
    EvidenceQualityStatus,
    Sentinel1ChangeResponse,
    Sentinel1ObservationDetail,
)
from app.services.data_collectors.google_earth_engine import gee_service
from app.services.quality.satellite_quality_service import satellite_quality_service


class Sentinel1ChangeService:
    """Evaluates multi-temporal Sentinel-1 C-band SAR GRD backscatter variations for surface change evidence."""

    def __init__(self, cache_ttl_seconds: int = 1800):
        # Bounded cache with TTL: (lat_round, lon_round, baseline_start, recent_end) -> (timestamp, response)
        self._cache: Dict[str, Tuple[float, Sentinel1ChangeResponse]] = {}
        self._cache_ttl = cache_ttl_seconds

    def _get_cache_key(
        self,
        lat: float,
        lon: float,
        baseline_days: int,
        recent_days: int,
    ) -> str:
        return f"{round(lat, 4)}_{round(lon, 4)}_{baseline_days}_{recent_days}"

    async def compute_s1_change(
        self,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        baseline_lookback_days: int = 60,
        recent_lookback_days: int = 15,
        force_refresh: bool = False,
    ) -> Sentinel1ChangeResponse:
        location = CoordinateLocation(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            state=state,
            district=district,
        )

        cache_key = self._get_cache_key(latitude, longitude, baseline_lookback_days, recent_lookback_days)
        if not force_refresh and cache_key in self._cache:
            ts, cached_res = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                return cached_res

        if not gee_service.is_initialized:
            gee_service.initialize()

        if not gee_service.is_initialized:
            res = Sentinel1ChangeResponse(
                location=location,
                is_valid_comparison=False,
                quality_status=EvidenceQualityStatus.PROVIDER_ERROR,
                missing_data_reasons=["Google Earth Engine authentication credentials not initialized or unavailable."],
            )
            return res

        now_utc = datetime.now(timezone.utc)
        recent_start = now_utc - timedelta(days=recent_lookback_days)
        baseline_start = now_utc - timedelta(days=baseline_lookback_days)
        baseline_end = recent_start

        def _fetch_and_compare():
            import ee
            point = ee.Geometry.Point([longitude, latitude])

            # Query recent collection
            recent_coll = (
                ee.ImageCollection("COPERNICUS/S1_GRD")
                .filterBounds(point)
                .filterDate(recent_start.strftime("%Y-%m-%d"), now_utc.strftime("%Y-%m-%d"))
                .filter(ee.Filter.eq("instrumentMode", "IW"))
                .sort("system:time_start", False)
            )

            recent_count = recent_coll.size().getInfo()
            if recent_count == 0:
                return {
                    "status": "NO_RECENT_PASSES",
                    "total_found": 0,
                    "reasons": [
                        f"Zero Sentinel-1 SAR IW passes found within recent window ({recent_start.strftime('%Y-%m-%d')} to {now_utc.strftime('%Y-%m-%d')})."
                    ],
                }

            # Select latest recent image
            recent_img = ee.Image(recent_coll.first())
            recent_orbit_pass = str(recent_img.get("orbitProperties_pass").getInfo() or "")
            recent_rel_orbit = recent_img.get("relativeOrbitNumber_start").getInfo()
            recent_time_ms = recent_img.get("system:time_start").getInfo()
            recent_id = str(recent_img.get("system:index").getInfo() or "")

            # Query baseline matching the same orbit pass direction for geometric consistency
            baseline_coll = (
                ee.ImageCollection("COPERNICUS/S1_GRD")
                .filterBounds(point)
                .filterDate(baseline_start.strftime("%Y-%m-%d"), baseline_end.strftime("%Y-%m-%d"))
                .filter(ee.Filter.eq("instrumentMode", "IW"))
            )

            if recent_orbit_pass:
                baseline_coll = baseline_coll.filter(ee.Filter.eq("orbitProperties_pass", recent_orbit_pass))

            baseline_count = baseline_coll.size().getInfo()
            if baseline_count == 0:
                return {
                    "status": "NO_MATCHING_BASELINE",
                    "total_found": recent_count,
                    "reasons": [
                        f"No geometrically compatible baseline SAR passes ({recent_orbit_pass or 'IW'}) found in period ({baseline_start.strftime('%Y-%m-%d')} to {baseline_end.strftime('%Y-%m-%d')})."
                    ],
                }

            baseline_img = ee.Image(baseline_coll.sort("system:time_start", False).first())
            baseline_orbit_pass = str(baseline_img.get("orbitProperties_pass").getInfo() or "")
            baseline_rel_orbit = baseline_img.get("relativeOrbitNumber_start").getInfo()
            baseline_time_ms = baseline_img.get("system:time_start").getInfo()
            baseline_id = str(baseline_img.get("system:index").getInfo() or "")

            # Reduce point values for both images
            recent_sample = (
                recent_img.select(["VV", "VH"] if "VH" in recent_img.bandNames().getInfo() else ["VV"])
                .reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=100000)
                .getInfo()
            )

            baseline_sample = (
                baseline_img.select(["VV", "VH"] if "VH" in baseline_img.bandNames().getInfo() else ["VV"])
                .reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=100000)
                .getInfo()
            )

            rec_vv = recent_sample.get("VV") if recent_sample else None
            rec_vh = recent_sample.get("VH") if recent_sample else None
            base_vv = baseline_sample.get("VV") if baseline_sample else None
            base_vh = baseline_sample.get("VH") if baseline_sample else None

            return {
                "status": "SUCCESS",
                "total_found": recent_count + baseline_count,
                "recent": {
                    "image_id": recent_id,
                    "time_ms": recent_time_ms,
                    "orbit_pass": recent_orbit_pass,
                    "rel_orbit": int(recent_rel_orbit) if recent_rel_orbit is not None else None,
                    "vv": round(float(rec_vv), 2) if rec_vv is not None else None,
                    "vh": round(float(rec_vh), 2) if rec_vh is not None else None,
                    "polarizations": ["VV", "VH"] if rec_vh is not None else ["VV"],
                },
                "baseline": {
                    "image_id": baseline_id,
                    "time_ms": baseline_time_ms,
                    "orbit_pass": baseline_orbit_pass,
                    "rel_orbit": int(baseline_rel_orbit) if baseline_rel_orbit is not None else None,
                    "vv": round(float(base_vv), 2) if base_vv is not None else None,
                    "vh": round(float(base_vh), 2) if base_vh is not None else None,
                    "polarizations": ["VV", "VH"] if base_vh is not None else ["VV"],
                },
            }

        try:
            raw = await asyncio.to_thread(_fetch_and_compare)
        except Exception as e:
            logger.warning(f"GEE S1 change detection failed for ({latitude}, {longitude}): {e}")
            res = Sentinel1ChangeResponse(
                location=location,
                is_valid_comparison=False,
                quality_status=EvidenceQualityStatus.PROVIDER_ERROR,
                missing_data_reasons=[f"Earth Engine query execution failed: {str(e)}"],
            )
            return res

        if raw["status"] != "SUCCESS":
            res = Sentinel1ChangeResponse(
                location=location,
                is_valid_comparison=False,
                quality_status=EvidenceQualityStatus.INSUFFICIENT_DATA,
                missing_data_reasons=raw.get("reasons", ["Insufficient Sentinel-1 passes found."]),
                valid_observations_count=raw.get("total_found", 0),
            )
            return res

        rec_data = raw["recent"]
        base_data = raw["baseline"]

        recent_dt = (
            datetime.fromtimestamp(rec_data["time_ms"] / 1000.0, tz=timezone.utc)
            if rec_data.get("time_ms")
            else None
        )
        baseline_dt = (
            datetime.fromtimestamp(base_data["time_ms"] / 1000.0, tz=timezone.utc)
            if base_data.get("time_ms")
            else None
        )

        recent_obs = Sentinel1ObservationDetail(
            image_id=rec_data.get("image_id"),
            acquisition_timestamp=recent_dt,
            orbit_direction=rec_data.get("orbit_pass"),
            relative_orbit_number=rec_data.get("rel_orbit"),
            polarization=rec_data.get("polarizations", ["VV"]),
            vv_backscatter_db=rec_data.get("vv"),
            vh_backscatter_db=rec_data.get("vh"),
        )

        baseline_obs = Sentinel1ObservationDetail(
            image_id=base_data.get("image_id"),
            acquisition_timestamp=baseline_dt,
            orbit_direction=base_data.get("orbit_pass"),
            relative_orbit_number=base_data.get("rel_orbit"),
            polarization=base_data.get("polarizations", ["VV"]),
            vv_backscatter_db=base_data.get("vv"),
            vh_backscatter_db=base_data.get("vh"),
        )

        # Evaluate quality & validity
        quality_status, is_valid, quality_reasons = (
            satellite_quality_service.evaluate_sentinel1_comparability(
                baseline_obs={
                    "orbit_direction": base_data.get("orbit_pass"),
                    "relative_orbit_number": base_data.get("rel_orbit"),
                    "vv_backscatter_db": base_data.get("vv"),
                },
                recent_obs={
                    "orbit_direction": rec_data.get("orbit_pass"),
                    "relative_orbit_number": rec_data.get("rel_orbit"),
                    "vv_backscatter_db": rec_data.get("vv"),
                },
                total_found=raw.get("total_found", 0),
            )
        )

        # Calculate Deltas if values exist
        delta_vv = None
        delta_vh = None
        if rec_data.get("vv") is not None and base_data.get("vv") is not None:
            delta_vv = round(rec_data["vv"] - base_data["vv"], 2)

        if rec_data.get("vh") is not None and base_data.get("vh") is not None:
            delta_vh = round(rec_data["vh"] - base_data["vh"], 2)

        freshness_hours, freshness_warnings = satellite_quality_service.evaluate_freshness_hours(recent_dt)
        all_reasons = quality_reasons + freshness_warnings

        response = Sentinel1ChangeResponse(
            location=location,
            baseline_observation=baseline_obs,
            recent_observation=recent_obs,
            delta_vv_db=delta_vv,
            delta_vh_db=delta_vh,
            valid_observations_count=raw.get("total_found", 0),
            is_valid_comparison=is_valid,
            quality_status=quality_status,
            missing_data_reasons=all_reasons,
            freshness_hours=freshness_hours,
        )

        # Store in cache
        self._cache[cache_key] = (time.time(), response)
        # Limit cache size to 100 entries
        if len(self._cache) > 100:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            self._cache.pop(oldest_key, None)

        return response


s1_change_service = Sentinel1ChangeService()

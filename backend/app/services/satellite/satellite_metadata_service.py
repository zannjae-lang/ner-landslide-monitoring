import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.schemas.satellite_evidence import (
    CoordinateLocation,
    EvidenceQualityStatus,
    SatelliteDatasetMetadata,
    SatelliteMetadataResponse,
)
from app.services.data_collectors.google_earth_engine import gee_service


class SatelliteMetadataService:
    """Extracts granular observation metadata from Google Earth Engine collections (Sentinel-1, Sentinel-2, Copernicus DEM)."""

    async def get_all_satellite_metadata(
        self,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
    ) -> SatelliteMetadataResponse:
        location = CoordinateLocation(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            state=state,
            district=district,
        )

        s1_task = self.get_sentinel1_metadata(latitude, longitude)
        s2_task = self.get_sentinel2_metadata(latitude, longitude)
        dem_task = self.get_dem_metadata(latitude, longitude)

        s1_meta, s2_meta, dem_meta = await asyncio.gather(s1_task, s2_task, dem_task)

        datasets = {
            "sentinel1_sar": s1_meta,
            "sentinel2_optical": s2_meta,
            "copernicus_dem": dem_meta,
        }

        # Determine overall status
        available_count = sum(1 for d in datasets.values() if d.is_available)
        summary_notes = []

        if available_count == 3:
            status = EvidenceQualityStatus.VALID
            summary_notes.append("All 3 satellite datasets actively queried and available.")
        elif available_count > 0:
            status = EvidenceQualityStatus.REQUIRES_VERIFICATION
            summary_notes.append(f"{available_count}/3 satellite datasets available at target coordinates.")
        else:
            status = (
                EvidenceQualityStatus.PROVIDER_ERROR
                if not gee_service.is_initialized
                else EvidenceQualityStatus.NOT_AVAILABLE
            )
            summary_notes.append("No satellite dataset observations available for the given coordinates.")

        return SatelliteMetadataResponse(
            location=location,
            generated_at=datetime.now(timezone.utc),
            status=status,
            datasets=datasets,
            summary_notes=summary_notes,
        )

    async def get_sentinel1_metadata(
        self,
        latitude: float,
        longitude: float,
        lookback_days: int = 60,
    ) -> SatelliteDatasetMetadata:
        if not gee_service.is_initialized:
            gee_service.initialize()

        if not gee_service.is_initialized:
            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/S1_GRD",
                provider="google_earth_engine",
                is_available=False,
                error_status="Google Earth Engine credentials not initialized.",
            )

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=lookback_days)

        def _fetch_s1_meta():
            import ee
            point = ee.Geometry.Point([longitude, latitude])
            coll = (
                ee.ImageCollection("COPERNICUS/S1_GRD")
                .filterBounds(point)
                .filterDate(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                .filter(ee.Filter.eq("instrumentMode", "IW"))
            )

            count = coll.size().getInfo()
            if count == 0:
                return SatelliteDatasetMetadata(
                    dataset_name="COPERNICUS/S1_GRD",
                    provider="google_earth_engine",
                    is_available=False,
                    quality_flags={"image_count": 0, "lookback_days": lookback_days},
                    error_status="No Sentinel-1 IW GRD passes found in recent time window.",
                )

            latest_img = ee.Image(coll.sort("system:time_start", False).first())
            img_id = latest_img.get("system:index").getInfo()
            time_start_ms = latest_img.get("system:time_start").getInfo()
            orbit_dir = latest_img.get("orbitProperties_pass").getInfo()
            rel_orbit = latest_img.get("relativeOrbitNumber_start").getInfo()
            polarizations = latest_img.get("transmitterReceiverPolarisation").getInfo()
            bands = latest_img.bandNames().getInfo()

            acq_dt = (
                datetime.fromtimestamp(time_start_ms / 1000.0, tz=timezone.utc)
                if time_start_ms
                else None
            )

            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/S1_GRD",
                provider="google_earth_engine",
                is_available=True,
                image_id=str(img_id) if img_id else None,
                acquisition_timestamp=acq_dt,
                orbit_direction=str(orbit_dir) if orbit_dir else None,
                relative_orbit_number=int(rel_orbit) if rel_orbit is not None else None,
                polarization=list(polarizations) if isinstance(polarizations, list) else ["VV", "VH"],
                available_bands=list(bands) if isinstance(bands, list) else ["VV", "VH"],
                spatial_resolution="10m (IW Ground Range Detected)",
                quality_flags={
                    "total_passes_found": count,
                    "instrument_mode": "IW",
                    "lookback_days": lookback_days,
                },
            )

        try:
            return await asyncio.to_thread(_fetch_s1_meta)
        except Exception as e:
            logger.warning(f"Failed to fetch Sentinel-1 metadata for ({latitude}, {longitude}): {e}")
            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/S1_GRD",
                provider="google_earth_engine",
                is_available=False,
                error_status=str(e),
            )

    async def get_sentinel2_metadata(
        self,
        latitude: float,
        longitude: float,
        lookback_days: int = 180,
    ) -> SatelliteDatasetMetadata:
        if not gee_service.is_initialized:
            gee_service.initialize()

        if not gee_service.is_initialized:
            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/S2_SR_HARMONIZED",
                provider="google_earth_engine",
                is_available=False,
                error_status="Google Earth Engine credentials not initialized.",
            )

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=lookback_days)

        def _fetch_s2_meta():
            import ee
            point = ee.Geometry.Point([longitude, latitude])
            coll = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(point)
                .filterDate(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            )

            count = coll.size().getInfo()
            if count == 0:
                return SatelliteDatasetMetadata(
                    dataset_name="COPERNICUS/S2_SR_HARMONIZED",
                    provider="google_earth_engine",
                    is_available=False,
                    quality_flags={"image_count": 0, "lookback_days": lookback_days},
                    error_status="No Sentinel-2 MSI Surface Reflectance granules found in time window.",
                )

            latest_img = ee.Image(coll.sort("system:time_start", False).first())
            img_id = latest_img.get("system:index").getInfo()
            time_start_ms = latest_img.get("system:time_start").getInfo()
            cloud_pct = latest_img.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()
            bands = latest_img.bandNames().getInfo()

            acq_dt = (
                datetime.fromtimestamp(time_start_ms / 1000.0, tz=timezone.utc)
                if time_start_ms
                else None
            )

            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/S2_SR_HARMONIZED",
                provider="google_earth_engine",
                is_available=True,
                image_id=str(img_id) if img_id else None,
                acquisition_timestamp=acq_dt,
                cloud_percentage=round(float(cloud_pct), 2) if cloud_pct is not None else None,
                available_bands=list(bands) if isinstance(bands, list) else ["B2", "B3", "B4", "B8", "B11", "B12"],
                spatial_resolution="10m (VNIR) - 20m (SWIR)",
                quality_flags={
                    "total_granules_found": count,
                    "processing_level": "Level-2A BOA Surface Reflectance",
                    "lookback_days": lookback_days,
                },
            )

        try:
            return await asyncio.to_thread(_fetch_s2_meta)
        except Exception as e:
            logger.warning(f"Failed to fetch Sentinel-2 metadata for ({latitude}, {longitude}): {e}")
            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/S2_SR_HARMONIZED",
                provider="google_earth_engine",
                is_available=False,
                error_status=str(e),
            )

    async def get_dem_metadata(
        self,
        latitude: float,
        longitude: float,
    ) -> SatelliteDatasetMetadata:
        if not gee_service.is_initialized:
            gee_service.initialize()

        if not gee_service.is_initialized:
            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/DEM/GLO30_2024_1",
                provider="google_earth_engine",
                is_available=False,
                error_status="Google Earth Engine credentials not initialized.",
            )

        def _fetch_dem_meta():
            import ee
            point = ee.Geometry.Point([longitude, latitude])
            coll = ee.ImageCollection("COPERNICUS/DEM/GLO30_2024_1").filterBounds(point)
            count = coll.size().getInfo()
            if count == 0:
                return SatelliteDatasetMetadata(
                    dataset_name="COPERNICUS/DEM/GLO30_2024_1",
                    provider="google_earth_engine",
                    is_available=False,
                    quality_flags={"tile_count": 0},
                    error_status="No Copernicus DEM GLO-30 tiles covering coordinate.",
                )

            first_tile = ee.Image(coll.first())
            img_id = first_tile.get("system:index").getInfo()

            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/DEM/GLO30_2024_1",
                provider="google_earth_engine",
                is_available=True,
                image_id=str(img_id) if img_id else "Copernicus_DSM_COG_10_N_E",
                spatial_resolution="30m Global DEM",
                available_bands=["DEM", "EDM", "FLM", "HEM", "WBM"],
                quality_flags={
                    "tile_count": count,
                    "datum": "WGS84 EGM2008 geoid",
                    "release_version": "2024_1",
                },
            )

        try:
            return await asyncio.to_thread(_fetch_dem_meta)
        except Exception as e:
            logger.warning(f"Failed to fetch Copernicus DEM metadata for ({latitude}, {longitude}): {e}")
            return SatelliteDatasetMetadata(
                dataset_name="COPERNICUS/DEM/GLO30_2024_1",
                provider="google_earth_engine",
                is_available=False,
                error_status=str(e),
            )


satellite_metadata_service = SatelliteMetadataService()

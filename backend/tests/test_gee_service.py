import asyncio
import pytest
from app.services.data_collectors.google_earth_engine import gee_service


def test_gee_initialization_and_health():
    async def run():
        ok, err = gee_service.initialize()
        assert ok is True, f"GEE failed to initialize: {err}"

        health = await gee_service.check_health()
        assert health["is_available"] is True
        assert "Live GEE Connected" in health["status"]
        assert health["latency_ms"] is not None

    asyncio.run(run())


def test_gee_copernicus_dem():
    async def run():
        # Test coordinates near Haflong, Assam (25.1764, 93.0189)
        res = await gee_service.get_dem_elevation(25.1764, 93.0189)
        assert res["status"] == "Success"
        assert res["elevation_m"] is not None
        assert res["elevation_m"] > 0
        assert res["dataset"] == "COPERNICUS/DEM/GLO30_2024_1"

    asyncio.run(run())


def test_gee_sentinel2_ndvi():
    async def run():
        res = await gee_service.get_sentinel2_ndvi(
            25.1764, 93.0189, start_date="2025-01-01", end_date="2025-12-31"
        )
        assert res["status"] == "Success"
        assert res["ndvi_p50"] is not None
        assert -1.0 <= res["ndvi_p50"] <= 1.0
        assert res["image_count"] > 0

    asyncio.run(run())


def test_gee_sentinel1_sar():
    async def run():
        res = await gee_service.get_sentinel1_sar(
            25.1764, 93.0189, start_date="2025-01-01", end_date="2025-12-31"
        )
        assert res["status"] == "Success"
        assert res["sar_backscatter_vv_db"] is not None
        assert res["image_count"] > 0

    asyncio.run(run())

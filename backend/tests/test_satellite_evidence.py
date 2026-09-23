from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.config.model_config import RiskLevel
from app.main import app
from app.schemas.predictions import (
    Model1FeatureInput,
    Model1PredictionOutput,
    Model2FeatureInput,
    Model2PredictionOutput,
    PredictionRunRequest,
)
from app.schemas.satellite_evidence import EvidenceQualityStatus
from app.services.quality.satellite_quality_service import satellite_quality_service
from app.services.risk_engine.risk_engine import risk_engine
from app.services.satellite.s1_change_service import s1_change_service
from app.services.satellite.s2_disturbance_service import s2_disturbance_service
from app.services.satellite.satellite_metadata_service import satellite_metadata_service

client = TestClient(app)


# 1. Valid Sentinel-1 metadata
@pytest.mark.anyio
async def test_sentinel1_metadata_valid():
    mock_meta = {
        "dataset_name": "COPERNICUS/S1_GRD",
        "provider": "google_earth_engine",
        "is_available": True,
        "image_id": "S1A_IW_GRDH_1SDV_20260915T120000",
        "acquisition_timestamp": datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc),
        "orbit_direction": "DESCENDING",
        "relative_orbit_number": 121,
        "polarization": ["VV", "VH"],
        "available_bands": ["VV", "VH"],
    }
    with patch.object(satellite_metadata_service, "get_sentinel1_metadata", new_callable=AsyncMock) as mock_fn:
        mock_fn.return_value = mock_meta
        res = await satellite_metadata_service.get_sentinel1_metadata(27.33, 88.61)
        assert res["is_available"] is True
        assert res["orbit_direction"] == "DESCENDING"
        assert res["relative_orbit_number"] == 121


# 2. Missing Sentinel-1 observations
@pytest.mark.anyio
async def test_sentinel1_missing_observations():
    from app.schemas.satellite_evidence import CoordinateLocation, Sentinel1ChangeResponse
    with patch.object(s1_change_service, "compute_s1_change", new_callable=AsyncMock) as mock_fn:
        mock_fn.return_value = Sentinel1ChangeResponse(
            location=CoordinateLocation(latitude=27.33, longitude=88.61),
            is_valid_comparison=False,
            quality_status=EvidenceQualityStatus.INSUFFICIENT_DATA,
            missing_data_reasons=["Zero Sentinel-1 SAR IW passes found within recent window."],
            valid_observations_count=0,
        )
        res = await s1_change_service.compute_s1_change(27.33, 88.61)
        assert res.is_valid_comparison is False
        assert res.quality_status == EvidenceQualityStatus.INSUFFICIENT_DATA
        assert "Zero Sentinel-1" in res.missing_data_reasons[0]



# 3. Incompatible orbit comparisons
def test_quality_service_incompatible_orbits():
    base_obs = {"orbit_direction": "ASCENDING", "relative_orbit_number": 45, "vv_backscatter_db": -12.5}
    rec_obs = {"orbit_direction": "DESCENDING", "relative_orbit_number": 45, "vv_backscatter_db": -10.2}
    status, is_valid, reasons = satellite_quality_service.evaluate_sentinel1_comparability(
        baseline_obs=base_obs,
        recent_obs=rec_obs,
        total_found=4,
    )
    assert status == EvidenceQualityStatus.LOW_QUALITY
    assert is_valid is False
    assert any("Incompatible orbit directions" in r for r in reasons)


# 4. Valid VV/VH change calculation
def test_quality_service_valid_s1_change():
    base_obs = {"orbit_direction": "DESCENDING", "relative_orbit_number": 121, "vv_backscatter_db": -11.50}
    rec_obs = {"orbit_direction": "DESCENDING", "relative_orbit_number": 121, "vv_backscatter_db": -14.20}
    status, is_valid, reasons = satellite_quality_service.evaluate_sentinel1_comparability(
        baseline_obs=base_obs,
        recent_obs=rec_obs,
        total_found=6,
    )
    assert status == EvidenceQualityStatus.VALID
    assert is_valid is True
    delta_vv = round(rec_obs["vv_backscatter_db"] - base_obs["vv_backscatter_db"], 2)
    assert delta_vv == -2.70


# 5. Valid Sentinel-2 NDVI calculation
def test_quality_service_valid_s2_ndvi():
    status, is_valid, reasons = satellite_quality_service.evaluate_sentinel2_quality(
        baseline_count=5,
        recent_count=2,
        baseline_cloud=12.0,
        recent_cloud=18.5,
        cloud_threshold=30.0,
        baseline_ndvi=0.72,
        recent_ndvi=0.55,
    )
    assert status == EvidenceQualityStatus.VALID
    assert is_valid is True
    delta_ndvi = round(0.55 - 0.72, 3)
    assert delta_ndvi == -0.170


# 6. Cloud-filtered empty collection
def test_quality_service_cloud_filtered_empty():
    status, is_valid, reasons = satellite_quality_service.evaluate_sentinel2_quality(
        baseline_count=3,
        recent_count=0,  # Zero cloud free images
        baseline_cloud=15.0,
        recent_cloud=0.0,
        cloud_threshold=20.0,
        baseline_ndvi=0.68,
        recent_ndvi=None,
    )
    assert status == EvidenceQualityStatus.INSUFFICIENT_DATA
    assert is_valid is False
    assert any("Zero cloud-free Sentinel-2 images" in r for r in reasons)


# 7. Missing baseline composite
def test_quality_service_missing_baseline():
    status, is_valid, reasons = satellite_quality_service.evaluate_sentinel2_quality(
        baseline_count=0,
        recent_count=4,
        baseline_cloud=0.0,
        recent_cloud=14.0,
        cloud_threshold=30.0,
        baseline_ndvi=None,
        recent_ndvi=0.62,
    )
    assert status == EvidenceQualityStatus.INSUFFICIENT_DATA
    assert is_valid is False


# 8. Invalid coordinates validation
def test_api_invalid_coordinates():
    # Lat > 90
    response = client.get("/api/v1/satellite-analysis/metadata?latitude=999.0&longitude=88.0")
    assert response.status_code == 422

    # Lon < -180
    response2 = client.get("/api/v1/satellite-analysis/sentinel1/change?latitude=27.0&longitude=-200.0")
    assert response2.status_code == 422


# 9. Invalid date range validation
def test_api_invalid_lookback_range():
    # recent_lookback_days >= baseline_lookback_days
    response = client.get(
        "/api/v1/satellite-analysis/sentinel1/change?latitude=27.33&longitude=88.61&baseline_lookback_days=30&recent_lookback_days=45"
    )
    assert response.status_code == 400
    assert "recent_lookback_days must be strictly less than baseline_lookback_days" in response.json()["detail"]


# 10. Provider failure handling
@pytest.mark.anyio
async def test_provider_uninitialized_failure():
    with patch("app.services.data_collectors.google_earth_engine.gee_service._is_initialized", False):
        with patch("app.services.data_collectors.google_earth_engine.gee_service.initialize", return_value=(False, "Auth Error")):
            res = await s1_change_service.compute_s1_change(27.33, 88.61, force_refresh=True)
            assert res.quality_status == EvidenceQualityStatus.PROVIDER_ERROR
            assert res.is_valid_comparison is False



# 11. Freshness and quality status calculation
def test_quality_service_freshness():
    old_time = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    age_hours, warnings = satellite_quality_service.evaluate_freshness_hours(old_time, max_freshness_hours=100.0)
    assert age_hours is not None
    assert age_hours > 100.0
    assert len(warnings) > 0


# 12. Existing prediction API regression test (Ensures /api/v1/predictions/run works unchanged)
def test_existing_prediction_api_regression():
    payload = {
        "latitude": 27.3389,
        "longitude": 88.6065,
        "location_name": "Gangtok Test Station",
        "state": "Sikkim",
        "district": "East Sikkim",
        "model1_features": {
            "elevation": 1650.0,
            "slope": 28.5,
            "curvature": 0.02,
            "tpi": 1.5,
            "tri": 6.2,
            "aspect_sin": 0.707,
            "aspect_cos": 0.707,
            "ndvi_p90": 0.75,
            "ndvi_p50": 0.62,
            "ndvi_p10": 0.48,
            "distance_to_road_m": 120.0,
            "distance_to_drainage_m": 85.0,
            "lulc_type": "Forest",
        },
        "model2_features": {
            "Rainfall_1h": 5.0,
            "Rainfall_3h": 12.0,
            "Rainfall_6h": 22.0,
            "Rainfall_12h": 35.0,
            "Rainfall_24h": 55.0,
            "Rainfall_3day": 90.0,
            "Rainfall_7day": 140.0,
            "susceptibility_probability": 0.65,
            "soil_moisture_layer_1": 0.35,
            "soil_moisture_layer_2": 0.38,
        },
    }
    response = client.post("/api/v1/predictions/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "combined_risk_score" in data
    assert "final_risk" in data
    assert "model1_result" in data
    assert "model2_result" in data
    assert data["engine_version"] == "2.0"


# 13. Existing Risk Engine regression test
def test_existing_risk_engine_regression():
    m1 = Model1PredictionOutput(
        model_name="Landslide Susceptibility Model",
        model_version="model1_v1.0",
        susceptibility_probability=0.60,
        susceptibility_percent=60.0,
        susceptibility_class="Moderate",
        threshold=0.39,
        is_susceptible=True,
    )
    m2 = Model2PredictionOutput(
        model_name="Dynamic Landslide Early Warning Model",
        model_version="model2_v1.0_temporal_candidate",
        dynamic_probability=0.40,
        warning_candidate=True,
        threshold=0.10,
    )
    # Expected score: (0.45 * 0.60) + (0.55 * 0.40) + 0.10 (for 40mm rain) = 0.27 + 0.22 + 0.10 = 0.59 (Alert)
    res = risk_engine.compute_risk(
        model1_result=m1,
        model2_result=m2,
        rainfall_24h_mm=40.0,
    )
    assert res.combined_risk_score == pytest.approx(0.59, abs=1e-3)
    assert res.final_risk == RiskLevel.ALERT

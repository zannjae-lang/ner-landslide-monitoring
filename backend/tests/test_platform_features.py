from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.config.model_config import RiskLevel
from app.main import app
from app.schemas.predictions import (
    Model1PredictionOutput,
    Model2PredictionOutput,
)
from app.services.evidence.evidence_service import evidence_service
from app.services.exposure.exposure_service import exposure_service
from app.services.exposure.route_risk_service import route_risk_service
from app.services.historical.replay_service import replay_service
from app.services.reporting.explainability_service import explainability_service
from app.services.risk_engine.risk_engine import risk_engine
from app.services.spatial.grid_service import grid_service

client = TestClient(app)


# 1. Evidence Fusion Evaluation
@pytest.mark.anyio
async def test_evidence_fusion_evaluation():
    payload = {
        "latitude": 27.3389,
        "longitude": 88.6065,
        "location_name": "Gangtok Ridge Test",
        "state": "Sikkim",
        "district": "East Sikkim",
        "include_satellite_check": False,
    }
    response = client.post("/api/v1/evidence/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "overall_evidence_score" in data
    assert "evidence_level" in data
    assert "factors" in data
    assert len(data["factors"]) >= 3
    assert data["is_provisional"] is True


# 2. Regional Hotspots Spatial Grid
def test_spatial_hotspots_endpoint():
    response = client.get("/api/v1/spatial/hotspots?state=Sikkim")
    assert response.status_code == 200
    data = response.json()
    assert "cells" in data
    assert data["total_cells"] >= 1
    assert any(c["state"] == "Sikkim" for c in data["cells"])


# 3. State Risk Summaries
def test_state_summaries_endpoint():
    response = client.get("/api/v1/spatial/states/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_states"] == 8
    assert len(data["states"]) == 8


# 4. District Vulnerability Rankings
def test_district_rankings_endpoint():
    response = client.get("/api/v1/spatial/district-rankings")
    assert response.status_code == 200
    data = response.json()
    assert "rankings" in data
    assert len(data["rankings"]) >= 5
    assert "composite_vulnerability_score" in data["rankings"][0]


# 5. Infrastructure Exposure Analysis
def test_exposure_analysis_endpoint():
    payload = {
        "latitude": 27.3389,
        "longitude": 88.6065,
        "location_name": "Gangtok Sector",
        "buffer_radius_meters": 1500.0,
    }
    response = client.post("/api/v1/exposure/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_exposed_assets" in data
    assert "exposed_assets" in data
    assert len(data["exposed_assets"]) >= 1


# 6. Critical Transport Corridors List & Corridor Risk
def test_corridor_risk_endpoint():
    corridors_res = client.get("/api/v1/exposure/corridors")
    assert corridors_res.status_code == 200
    corridors = corridors_res.json()
    assert len(corridors) >= 3

    # Run Corridor Risk for NH-10 Sikkim
    payload = {"corridor_id": "NH_10_SK", "buffer_distance_meters": 500.0}
    risk_res = client.post("/api/v1/exposure/corridor-risk", json=payload)
    assert risk_res.status_code == 200
    c_data = risk_res.json()
    assert c_data["corridor_id"] == "NH_10_SK"
    assert c_data["total_segments"] >= 3
    assert "max_segment_risk" in c_data


# 7. Explainable AI Risk Report
def test_explainable_report_generation():
    payload = {
        "latitude": 27.3389,
        "longitude": 88.6065,
        "location_name": "Gangtok Explainability Test",
        "state": "Sikkim",
        "district": "East Sikkim",
    }
    response = client.post("/api/v1/reports/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "model1_susceptibility_explainability" in data
    assert "model2_dynamic_explainability" in data
    assert "executive_summary_narrative" in data
    assert "key_risk_drivers" in data


# 8. Historical Disaster Event Replay
def test_historical_replay_catalog_and_simulation():
    cat_res = client.get("/api/v1/replay/events")
    assert cat_res.status_code == 200
    events = cat_res.json()["events"]
    assert len(events) >= 3

    # Simulate 2024 Cyclone Remal
    sim_res = client.post("/api/v1/replay/simulate/EVT_REMAL_2024")
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["event_details"]["event_id"] == "EVT_REMAL_2024"
    assert len(sim_data["timeline"]) == 7
    assert sim_data["peak_combined_risk_score"] > 0.40


# 9. Field Evidence Reporting & DDMA Triage
def test_field_report_lifecycle():
    report_payload = {
        "latitude": 25.6751,
        "longitude": 94.1086,
        "location_name": "Kohima South Slope",
        "state": "Nagaland",
        "district": "Kohima",
        "reporter_name": "Sub-Divisional Geologist",
        "reporter_role": "geologist",
        "observation_category": "VISIBLE_CRACK",
        "severity": "High",
        "description": "Observed 15cm tension crack opening along retaining wall embankment.",
    }
    create_res = client.post("/api/v1/field-reports", json=report_payload)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["verification_status"] == "submitted"
    report_id = created["id"]

    # DDMA Review Update
    patch_payload = {
        "verification_status": "verified",
        "reviewer_notes": "Field team confirmed active tension crack; alerted PWD engineers.",
        "reviewed_by": "DDMA Incident Commander",
    }
    patch_res = client.patch(f"/api/v1/field-reports/{report_id}", json=patch_payload)
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["verification_status"] == "verified"
    assert updated["reviewed_by"] == "DDMA Incident Commander"


# 10. Operational Health Telemetry
def test_operational_telemetry_endpoint():
    response = client.get("/api/v1/monitoring/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "overall_health_grade" in data
    assert "providers" in data
    assert "models" in data

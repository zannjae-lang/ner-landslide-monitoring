def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["Healthy", "Degraded"]
    assert data["model_readiness"] is True


def test_models_status_endpoint(client):
    res = client.get("/api/v1/models/status")
    assert res.status_code == 200
    data = res.json()
    assert data["is_ready"] is True
    assert "model1" in data["models"]
    assert "model2" in data["models"]


def test_locations_list(client):
    res = client.get("/api/v1/locations")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0


def test_prediction_run(client):
    payload = {
        "latitude": 27.0844,
        "longitude": 93.6053,
        "state": "Arunachal Pradesh",
        "district": "Papum Pare",
        "location_name": "Itanagar Station",
    }
    res = client.post("/api/v1/predictions/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["final_risk"] in ["Normal", "Watch", "Alert", "Critical"]
    assert 0.0 <= data["combined_risk_score"] <= 1.0
    assert data["model1_result"] is not None
    assert data["model2_result"] is not None


def test_map_risk_layer(client):
    res = client.get("/api/v1/map/risk")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0

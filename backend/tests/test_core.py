def test_health_returns_ok_and_counts(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "model_loaded" in body
    assert body["road_count"] >= 1
    assert body["poi_count"] >= 1
    assert body["active_scenario_id"] is not None


def test_meta_area_shape(client):
    response = client.get("/api/meta/area")
    assert response.status_code == 200
    body = response.json()
    assert body["name"]
    assert len(body["bbox"]) == 4
    assert len(body["default_center"]) == 2
    assert "disclaimer" in body


def test_login_success_and_failure(client):
    ok = client.post("/api/auth/login", json={"username": "reporter", "password": "reporter123"})
    assert ok.status_code == 200
    body = ok.json()
    assert body["token_type"] == "Bearer"
    assert body["user"]["role"] == "reporter"
    assert body["access_token"]

    bad = client.post("/api/auth/login", json={"username": "reporter", "password": "wrongpass"})
    assert bad.status_code == 401
    assert bad.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_scenarios_and_pois(client):
    scenarios = client.get("/api/scenarios").json()
    assert len(scenarios) >= 4
    assert {"id", "name", "description", "rainfall_mm_24h", "rainfall_mm_1h", "source", "is_active"} <= set(scenarios[0])

    pois = client.get("/api/pois").json()
    assert len(pois) >= 4
    assert {"id", "external_id", "name", "category", "lat", "lon", "status"} <= set(pois[0])

    hospitals = client.get("/api/pois", params={"category": "hospital"}).json()
    assert all(item["category"] == "hospital" for item in hospitals)


def test_map_geojson_frozen_road_fields(client):
    response = client.get("/api/map/geojson")
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    road = next(feature for feature in body["features"] if feature["properties"]["layer_type"] == "road")
    props = road["properties"]
    assert {
        "layer_type",
        "segment_id",
        "name",
        "road_type",
        "current_risk_score",
        "current_risk_level",
        "predicted_time_to_high_risk_min",
        "blocked",
        "flood_status",
    } <= set(props)


def test_blocked_report_requires_auth_and_verify_is_admin(client):
    public = client.post("/api/reports/blocked", json={"segment_id": 4, "note": "test"})
    assert public.status_code == 401

    reporter = client.post("/api/auth/login", json={"username": "reporter", "password": "reporter123"}).json()
    created = client.post(
        "/api/reports/blocked",
        json={"segment_id": 4, "source": "field_official", "note": "Waterlogging (placeholder)", "flood_status": "confirmed_flooded"},
        headers={"Authorization": f"Bearer {reporter['access_token']}"},
    )
    assert created.status_code in {200, 201}
    payload = created.json()
    assert payload["verification_status"] == "confirmed"
    assert payload["road_status"]["blocked"] is True

    active = client.get("/api/reports/active").json()
    assert any(item["segment_id"] == 4 for item in active)

    reporter_verify = client.post(
        f"/api/reports/{payload['report_id']}/verify",
        json={"decision": "confirm"},
        headers={"Authorization": f"Bearer {reporter['access_token']}"},
    )
    assert reporter_verify.status_code == 403

    admin = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()
    verified = client.post(
        f"/api/reports/{payload['report_id']}/verify",
        json={"decision": "confirm"},
        headers={"Authorization": f"Bearer {admin['access_token']}"},
    )
    assert verified.status_code == 200
    assert verified.json()["verification_status"] == "confirmed"

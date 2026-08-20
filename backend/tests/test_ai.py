from app.ai.predict import fallback_propensity, model_is_loaded, predict_static_propensity
from app.services.types import RoadSegment


def _segment(**overrides) -> RoadSegment:
    payload = {
        "id": 1,
        "from_node_id": 1,
        "to_node_id": 2,
        "length_m": 100.0,
        "geometry": [[80.21, 12.98], [80.211, 12.981]],
        "drainage_proxy": 0.4,
        "ml_static_propensity": 0.7,
    }
    payload.update(overrides)
    return RoadSegment(**payload)


def test_health_and_validation_include_ai_status(client):
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["model_loaded"] is False

    summary = client.get("/api/validation/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert {
        "model_loaded",
        "model_type",
        "segment_count",
        "risk_distribution",
        "top_high_risk_segments",
        "documented_flood_pockets",
    } <= set(body)
    assert body["segment_count"] >= 1
    assert "low" in body["risk_distribution"]


def test_recompute_risk_requires_admin(client):
    public = client.post("/api/admin/recompute-risk")
    assert public.status_code == 401

    reporter = client.post("/api/auth/login", json={"username": "reporter", "password": "reporter123"}).json()
    forbidden = client.post(
        "/api/admin/recompute-risk",
        headers={"Authorization": f"Bearer {reporter['access_token']}"},
    )
    assert forbidden.status_code == 403

    admin = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()
    ok = client.post(
        "/api/admin/recompute-risk",
        headers={"Authorization": f"Bearer {admin['access_token']}"},
    )
    assert ok.status_code == 200
    body = ok.json()
    assert body["segments_updated"] >= 1
    assert "scenario_id" in body


def test_heuristic_propensity_uses_stored_then_drainage():
    assert model_is_loaded() is False
    stored = _segment(ml_static_propensity=0.88, drainage_proxy=0.2)
    assert predict_static_propensity(stored) == 0.88
    drainage = _segment(ml_static_propensity=None, drainage_proxy=0.31)
    assert fallback_propensity(drainage) == 0.31
    assert predict_static_propensity(drainage) == 0.31

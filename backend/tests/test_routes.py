from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_route_uses_frozen_response_shape():
    response = client.post(
        "/api/routes",
        json={
            "origin": {"lat": 12.9800, "lon": 80.2100},
            "destination": {"poi_id": 1},
            "route_mode": "compare",
            "scenario_id": 3,
            "include_alternatives": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"request_id", "destination", "routes", "warnings", "explanation"}
    assert body["destination"]["type"] == "poi"
    assert {route["route_type"] for route in body["routes"]} == {"safe", "short"}
    assert set(body["routes"][0]) == {
        "route_type",
        "distance_m",
        "duration_min",
        "cost_score",
        "avg_risk_score",
        "high_risk_segments_count",
        "blocked_segments_encountered",
        "predicted_risk_warnings_count",
        "geometry",
    }


def test_reroute_accepts_current_location():
    response = client.post(
        "/api/routes/re-route",
        json={
            "current_location": {"lat": 12.9810, "lon": 80.2110},
            "destination": {"lat": 12.9820, "lon": 80.2150},
            "reason": "blocked_ahead",
            "route_mode": "safe",
            "scenario_id": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["routes"][0]["route_type"] == "safe"


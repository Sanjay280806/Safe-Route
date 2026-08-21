def _login(client, username: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_local_risk_rainfall_and_shelter_operations(client):
    admin_token = _login(client, "admin", "admin123")
    reporter_token = _login(client, "reporter", "reporter123")

    summary = client.get("/api/validation/summary")
    assert summary.status_code == 200
    assert summary.json()["model_loaded"] is True
    assert summary.json()["segment_count"] >= 1

    recomputed = client.post("/api/admin/recompute-risk", headers={"Authorization": f"Bearer {admin_token}"})
    assert recomputed.status_code == 200
    assert recomputed.json()["segments_updated"] >= 1

    rainfall = client.put(
        "/api/admin/rainfall",
        json={"rainfall_mm_24h": 95, "rainfall_mm_1h": 20},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert rainfall.status_code == 200
    assert rainfall.json()["rainfall_mm_24h"] == 95

    shelters = client.get("/api/shelters")
    assert shelters.status_code == 200
    shelter = shelters.json()[0]
    occupancy = client.patch(
        f"/api/shelters/{shelter['poi_id']}/occupancy",
        json={"occupancy_assumed": 12, "status": "open"},
        headers={"Authorization": f"Bearer {reporter_token}"},
    )
    assert occupancy.status_code == 200
    assert occupancy.json()["occupancy_assumed"] == 12


def test_resident_message_can_be_managed_by_control_room(client):
    created = client.post(
        "/api/messages",
        json={"sender_name": "Resident", "category": "road_blockage", "message": "Water across the local road", "segment_id": 1},
    )
    assert created.status_code == 201
    message = created.json()
    assert message["status"] == "open"

    reporter_token = _login(client, "reporter", "reporter123")
    inbox = client.get("/api/messages", headers={"Authorization": f"Bearer {reporter_token}"})
    assert inbox.status_code == 200
    assert any(item["id"] == message["id"] for item in inbox.json())

    updated = client.patch(
        f"/api/messages/{message['id']}",
        json={"status": "in_review"},
        headers={"Authorization": f"Bearer {reporter_token}"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "in_review"

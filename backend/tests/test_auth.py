def test_health_route(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["ok"] is True

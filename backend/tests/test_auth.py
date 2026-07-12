def test_health_route(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["ok"] is True


def test_activate_code(client):
    from backend.database import db

    db.execute("DELETE FROM users")
    activation_code = "123456"
    db.execute(
        "INSERT INTO users (full_name, email, password_hash, activated, activation_token, role) VALUES (?, ?, ?, ?, ?, ?)",
        ("OTP Tester", "otp@example.com", "dummy-hash", 0, activation_code, "student"),
    )

    response = client.post("/api/activate", json={"code": activation_code})

    assert response.status_code == 200
    assert response.json["ok"] is True
    assert "activated" in response.json["message"].lower()

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


def test_login_unactivated_account_returns_pending_activation(client):
    from backend.database import db
    from backend.security import make_password_hash

    db.execute("DELETE FROM users")
    db.execute(
        "INSERT INTO users (full_name, email, password_hash, activated, role) VALUES (?, ?, ?, ?, ?)",
        ("Pending Login", "pending-login@example.com", make_password_hash("password123"), 0, "student"),
    )

    response = client.post(
        "/api/login",
        json={"email": "pending-login@example.com", "password": "password123"},
    )

    assert response.status_code == 403
    assert response.json["pending_activation"] is True
    assert "activation" in response.json["error"].lower()


def test_me_reports_activation_status(client):
    from auth import create_session
    from backend.database import db

    db.execute("DELETE FROM users")
    user_id = db.execute(
        "INSERT INTO users (full_name, email, password_hash, activated, role) VALUES (?, ?, ?, ?, ?)",
        ("Me Tester", "me-tester@example.com", "dummy-hash", 0, "student"),
    )
    client.set_cookie("pfw_session", create_session(user_id))

    response = client.get("/api/me")

    assert response.status_code == 200
    assert response.json["activated"] == 0

"""
Tests for the reflections endpoint (/api/reflections).

Covers:
  - Creating a reflection with valid data (201).
  - Missing title or body (400).
  - Title exceeding the length limit (400).
  - Listing only the current user's reflections.
"""

from auth import create_session
from backend.database import db


def _make_activated_user(full_name, email):
    from security import make_password_hash

    db.execute(
        """INSERT INTO users (full_name, email, password_hash, activated, is_public, role)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (full_name, email, make_password_hash("testpass123"), 1, 1, "student"),
    )
    return db.fetchone("SELECT id FROM users WHERE email = ?", (email,))["id"]


def _login(client, user_id):
    client.set_cookie("pfw_session", create_session(user_id))


def test_create_reflection(client):
    db.execute("DELETE FROM users")
    user_id = _make_activated_user("Reflector", "reflector@example.com")
    _login(client, user_id)

    response = client.post(
        "/api/reflections",
        json={"title": "My first thought", "body": "This is a reflection.", "mood": "thoughtful"},
    )
    assert response.status_code == 201
    assert "id" in response.json


def test_create_reflection_missing_fields(client):
    db.execute("DELETE FROM users")
    user_id = _make_activated_user("Reflector", "reflector@example.com")
    _login(client, user_id)

    response = client.post("/api/reflections", json={"title": "", "body": ""})
    assert response.status_code == 400
    assert "error" in response.json


def test_create_reflection_title_too_long(client):
    db.execute("DELETE FROM users")
    user_id = _make_activated_user("Reflector", "reflector@example.com")
    _login(client, user_id)

    response = client.post(
        "/api/reflections",
        json={"title": "x" * 281, "body": "body"},
    )
    assert response.status_code == 400
    assert "error" in response.json


def test_list_only_own_reflections(client):
    db.execute("DELETE FROM users")
    user_a = _make_activated_user("User A", "a@example.com")
    user_b = _make_activated_user("User B", "b@example.com")

    _login(client, user_a)
    client.post("/api/reflections", json={"title": "A's note", "body": "private"})

    _login(client, user_b)
    client.post("/api/reflections", json={"title": "B's note", "body": "private"})

    response = client.get("/api/reflections")
    assert response.status_code == 200
    titles = [r["title"] for r in response.json]
    assert titles == ["B's note"]

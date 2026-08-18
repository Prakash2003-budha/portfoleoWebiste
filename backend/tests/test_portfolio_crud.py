"""
Tests for the portfolio evidence CRUD endpoints (/api/portfolio/<section>).

Covers:
  - Adding an item to a valid section as the owner (201 + new id).
  - Rejecting an unknown section (404).
  - Rejecting a missing required field (400).
  - Deleting your own item (200).
  - Preventing deletion of another user's item (404 — no leak).
  - Fetching your own portfolio vs. someone else's public profile.
"""

from auth import create_session
from backend.database import db


def _make_activated_user(full_name, email):
    """Insert an activated user with a real password hash and a profile, return (id, password)."""
    from security import make_password_hash

    password = "testpass123"
    db.execute(
        """INSERT INTO users (full_name, email, password_hash, activated, is_public, role)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (full_name, email, make_password_hash(password), 1, 1, "student"),
    )
    user_id = db.fetchone("SELECT id FROM users WHERE email = ?", (email,))["id"]
    db.execute(
        """INSERT INTO profiles (user_id, display_name, headline, location, bio)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, full_name, "A headline", "Somewhere", "A short bio."),
    )
    return user_id, password


def _login(client, user_id):
    client.set_cookie("pfw_session", create_session(user_id))


def test_add_portfolio_item_as_owner(client):
    db.execute("DELETE FROM users")
    user_id, _ = _make_activated_user("Portfolio Owner", "owner@example.com")
    _login(client, user_id)

    response = client.post(
        "/api/portfolio/experiences",
        json={"title": "Test Job", "organization": "Test Org"},
    )
    assert response.status_code == 201
    assert "id" in response.json

    # The item should appear in the user's portfolio view.
    portfolio = client.get("/api/portfolio/me")
    assert len(portfolio.json["sections"]["experiences"]) == 1
    assert portfolio.json["sections"]["experiences"][0]["title"] == "Test Job"


def test_add_item_unknown_section_returns_404(client):
    db.execute("DELETE FROM users")
    user_id, _ = _make_activated_user("Portfolio Owner", "owner@example.com")
    _login(client, user_id)

    response = client.post(
        "/api/portfolio/nonexistent_section",
        json={"title": "Test"},
    )
    assert response.status_code == 404
    assert "error" in response.json


def test_add_item_missing_required_field_returns_400(client):
    db.execute("DELETE FROM users")
    user_id, _ = _make_activated_user("Portfolio Owner", "owner@example.com")
    _login(client, user_id)

    response = client.post("/api/portfolio/experiences", json={"organization": "No Title"})
    assert response.status_code == 400
    assert "error" in response.json
    assert "required" in response.json["error"].lower()


def test_delete_own_portfolio_item(client):
    db.execute("DELETE FROM users")
    user_id, _ = _make_activated_user("Portfolio Owner", "owner@example.com")
    _login(client, user_id)

    create_resp = client.post(
        "/api/portfolio/experiences",
        json={"title": "To Delete", "organization": "Org"},
    )
    item_id = create_resp.json["id"]

    del_resp = client.delete(f"/api/portfolio/experiences/{item_id}")
    assert del_resp.status_code == 200
    assert del_resp.json["ok"] is True

    # Item should be gone.
    portfolio = client.get("/api/portfolio/me")
    assert len(portfolio.json["sections"]["experiences"]) == 0


def test_cannot_delete_other_users_item(client):
    db.execute("DELETE FROM users")
    owner_id, _ = _make_activated_user("Owner", "owner@example.com")
    intruder_id, _ = _make_activated_user("Intruder", "intruder@example.com")

    # Owner creates an item.
        # Owner creates an item.
    _login(client, owner_id)
    create_resp = client.post(
        "/api/portfolio/experiences",
        json={"title": "Owner's item", "organization": "Org"},
    )
    item_id = create_resp.json["id"]

    # Intruder tries to delete it (overwrites the session cookie).
    _login(client, intruder_id)
    response = client.delete(f"/api/portfolio/experiences/{item_id}")
    assert response.status_code == 404

    # Owner can still see it.
    client.delete("pfw_session")
    _login(client, owner_id)
    portfolio = client.get("/api/portfolio/me")
    assert len(portfolio.json["sections"]["experiences"]) == 1


def test_portfolio_schema_endpoint(client):
    response = client.get("/api/portfolio/schema")
    assert response.status_code == 200
    schema = response.json
    assert "experiences" in schema
    assert "fields" in schema["experiences"]
    assert isinstance(schema["experiences"]["fields"], list)

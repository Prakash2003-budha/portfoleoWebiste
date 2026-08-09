"""
Tests that accounts which have registered but not yet activated are NOT
visible anywhere public (profile directory, profile detail, portfolio,
posts), and that they become visible once their account is activated.
"""

from backend.database import db


def _create_user_with_content(email, full_name, activated):
    """Insert a user (and their profile + portfolio content) directly so the
    test doesn't depend on SMTP being configured for the /api/register flow."""
    db.execute(
        """INSERT INTO users (full_name, email, password_hash, activated, role)
           VALUES (?, ?, ?, ?, ?)""",
        (full_name, email, "dummy-hash", 1 if activated else 0, "student"),
    )
    user = db.fetchone("SELECT id FROM users WHERE email = ?", (email,))
    user_id = user["id"]

    db.execute(
        """INSERT INTO profiles (user_id, display_name, headline, location, bio)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, full_name, "A pending headline", "Somewhere", "A bio."),
    )
    profile = db.fetchone("SELECT id FROM profiles WHERE user_id = ?", (user_id,))
    profile_id = profile["id"]

    db.execute(
        """INSERT INTO experiences (user_id, title, organization) VALUES (?, ?, ?)""",
        (user_id, "Some Job", "Some Org"),
    )
    db.execute(
        """INSERT INTO posts (user_id, title, canvas_json, thumbnail)
           VALUES (?, ?, ?, ?)""",
        (user_id, "A post", "{}", "data:image/svg+xml;base64,PHN2Zy8+"),
    )
    return user_id, profile_id


def test_unactivated_user_not_in_public_directory(client):
    db.execute("DELETE FROM users")
    _create_user_with_content("pending@example.com", "Pending User", activated=False)

    response = client.get("/api/profiles")

    assert response.status_code == 200
    assert response.json == []


def test_unactivated_user_profile_and_portfolio_hidden(client):
    db.execute("DELETE FROM users")
    user_id, profile_id = _create_user_with_content(
        "pending@example.com", "Pending User", activated=False
    )

    assert client.get(f"/api/profiles/{profile_id}").status_code == 404
    assert client.get(f"/api/portfolio/user/{user_id}").status_code == 404
    assert client.get(f"/api/posts/user/{user_id}").json == []
    assert client.get("/api/posts").json == []


def test_activated_user_becomes_visible(client):
    db.execute("DELETE FROM users")
    user_id, profile_id = _create_user_with_content(
        "pending@example.com", "Pending User", activated=False
    )

    assert client.get("/api/profiles").json == []

    db.execute("UPDATE users SET activated = 1 WHERE id = ?", (user_id,))

    profiles = client.get("/api/profiles").json
    assert len(profiles) == 1
    assert profiles[0]["user_id"] == user_id

    profile_detail = client.get(f"/api/profiles/{profile_id}")
    assert profile_detail.status_code == 200
    assert profile_detail.json["user_id"] == user_id

    portfolio = client.get(f"/api/portfolio/user/{user_id}")
    assert portfolio.status_code == 200
    assert portfolio.json["owner"]["user_id"] == user_id
    assert len(portfolio.json["sections"]["experiences"]) == 1

    posts = client.get(f"/api/posts/user/{user_id}").json
    assert len(posts) == 1
    assert posts[0]["title"] == "A post"

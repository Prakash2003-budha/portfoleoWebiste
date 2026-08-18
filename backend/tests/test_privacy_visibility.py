"""
Tests for the account privacy toggle (users.is_public).

Rules enforced:
- Public accounts (activated AND is_public = 1) are visible to everyone.
- Private accounts (activated but is_public = 0) are hidden from everyone
  except their owner -- profile detail, portfolio, and posts all return the
  same "not found" / empty responses as an unactivated account, and the
  profile drops out of the public directory.
- The owner can still see and edit their own private profile/portfolio/posts,
  and can flip the toggle back to public.
"""

from auth import create_session
from backend.database import db


def _create_user_with_content(email, full_name, is_public):
    db.execute(
        """INSERT INTO users (full_name, email, password_hash, activated, is_public, role)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (full_name, email, "dummy-hash", 1, 1 if is_public else 0, "student"),
    )
    user = db.fetchone("SELECT id FROM users WHERE email = ?", (email,))
    user_id = user["id"]

    db.execute(
        """INSERT INTO profiles (user_id, display_name, headline, location, bio)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, full_name, "A headline", "Somewhere", "A bio."),
    )
    profile_id = db.fetchone("SELECT id FROM profiles WHERE user_id = ?", (user_id,))["id"]

    db.execute(
        """INSERT INTO experiences (user_id, title, organization) VALUES (?, ?, ?)""",
        (user_id, "Some Job", "Some Org"),
    )
    db.execute(
        """INSERT INTO posts (user_id, title, canvas_json, thumbnail)
           VALUES (?, ?, ?, ?)""",
        (user_id, "A post", "{}", "data:image/svg+xml;base64,PHN2Zy8+"),
    )
    post_id = db.fetchone("SELECT id FROM posts WHERE user_id = ?", (user_id,))["id"]
    return user_id, profile_id, post_id


def _login(client, user_id):
    """Attach a valid session cookie for the given user to the test client."""
    client.set_cookie("pfw_session", create_session(user_id))


def test_private_user_hidden_from_anonymous(client, app):
    db.execute("DELETE FROM users")
    user_id, profile_id, post_id = _create_user_with_content(
        "private@example.com", "Private User", is_public=False
    )
    anon = app.test_client()

    assert anon.get("/api/profiles").json == []
    assert anon.get(f"/api/profiles/{profile_id}").status_code == 404
    assert anon.get(f"/api/portfolio/user/{user_id}").status_code == 404
    assert anon.get(f"/api/posts/user/{user_id}").json == []
    assert anon.get(f"/api/posts/{post_id}").status_code == 404
    assert anon.get("/api/posts").json == []


def test_private_user_hidden_from_other_logged_in_user(client):
    db.execute("DELETE FROM users")
    user_id, profile_id, _ = _create_user_with_content(
        "private@example.com", "Private User", is_public=False
    )
    other_id, _, _ = _create_user_with_content(
        "other@example.com", "Other User", is_public=True
    )
    _login(client, other_id)

    assert client.get(f"/api/profiles/{profile_id}").status_code == 404
    assert client.get(f"/api/portfolio/user/{user_id}").status_code == 404
    assert client.get(f"/api/posts/user/{user_id}").json == []


def test_private_user_owner_still_sees_everything(client):
    db.execute("DELETE FROM users")
    user_id, profile_id, post_id = _create_user_with_content(
        "private@example.com", "Private User", is_public=False
    )
    _login(client, user_id)

    # The owner's own profile is not in the public directory either.
    assert client.get("/api/profiles").json == []

    detail = client.get(f"/api/profiles/{profile_id}")
    assert detail.status_code == 200
    assert detail.json["is_owner"] is True
    assert detail.json["is_public"] == 0

    portfolio = client.get(f"/api/portfolio/user/{user_id}")
    assert portfolio.status_code == 200
    assert len(portfolio.json["sections"]["experiences"]) == 1

    posts = client.get(f"/api/posts/user/{user_id}").json
    assert len(posts) == 1
    assert posts[0]["is_owner"] is True

    post_detail = client.get(f"/api/posts/{post_id}")
    assert post_detail.status_code == 200
    assert "canvas_json" in post_detail.json  # owner gets the editable canvas


def test_owner_can_toggle_privacy_via_profile_save(client, app):
    db.execute("DELETE FROM users")
    user_id, profile_id, _ = _create_user_with_content(
        "private@example.com", "Private User", is_public=True
    )
    anon = app.test_client()

    # Public by default -- anonymous can see the profile.
    assert anon.get(f"/api/profiles/{profile_id}").status_code == 200
    assert len(anon.get("/api/profiles").json) == 1

    _login(client, user_id)
    resp = client.put(
        "/api/profile/me",
        json={"display_name": "Private User", "headline": "A headline", "is_public": False},
    )
    assert resp.status_code == 200

    # /me now reports the new state.
    assert client.get("/api/me").json["is_public"] == 0

    # Anonymous is locked out everywhere; the owner still gets in.
    assert anon.get(f"/api/profiles/{profile_id}").status_code == 404
    assert anon.get(f"/api/portfolio/user/{user_id}").status_code == 404
    assert anon.get(f"/api/posts/user/{user_id}").json == []
    assert len(anon.get("/api/profiles").json) == 0
    assert client.get(f"/api/profiles/{profile_id}").status_code == 200

    # Flipping back to public restores visibility for everyone.
    client.put(
        "/api/profile/me",
        json={"display_name": "Private User", "headline": "A headline", "is_public": True},
    )
    assert anon.get(f"/api/profiles/{profile_id}").status_code == 200
    assert len(anon.get("/api/profiles").json) == 1

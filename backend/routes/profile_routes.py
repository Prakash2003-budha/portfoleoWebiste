from flask import Blueprint, jsonify, request

from auth import current_user, login_required
from database import db

bp = Blueprint("profiles", __name__, url_prefix="/api")


@bp.get("/profiles")
def list_profiles():
    user = current_user()
    rows = db.fetchall(
        """SELECT profiles.*, users.full_name
           FROM profiles JOIN users ON users.id = profiles.user_id
           ORDER BY profiles.id DESC"""
    )
    for row in rows:
        row["is_owner"] = bool(user) and row["user_id"] == user["id"]
    return jsonify(rows)


@bp.get("/profiles/<int:profile_id>")
def get_profile(profile_id):
    row = db.fetchone(
        """SELECT profiles.*, users.full_name, users.email
           FROM profiles JOIN users ON users.id = profiles.user_id
           WHERE profiles.id = ?""",
        (profile_id,),
    )
    if not row:
        return jsonify({"error": "Profile not found."}), 404
    user = current_user()
    row["is_owner"] = bool(user) and row["user_id"] == user["id"]
    return jsonify(row)


@bp.get("/profile/me")
@login_required
def my_profile(user):
    row = db.fetchone("SELECT * FROM profiles WHERE user_id = ?", (user["id"],))
    return jsonify(row or {})


@bp.put("/profile/me")
@login_required
def save_profile(user):
    data = request.get_json(silent=True) or {}
    display_name = (data.get("display_name") or "").strip()
    headline = (data.get("headline") or "").strip()
    location = (data.get("location") or "").strip()
    bio = (data.get("bio") or "").strip()

    if not display_name or not headline:
        return jsonify({"error": "Display name and headline are required."}), 400

    existing = db.fetchone("SELECT id FROM profiles WHERE user_id = ?", (user["id"],))
    if existing:
        db.execute(
            "UPDATE profiles SET display_name = ?, headline = ?, location = ?, bio = ? WHERE user_id = ?",
            (display_name, headline, location, bio, user["id"]),
        )
        profile_id = existing["id"]
    else:
        profile_id = db.execute(
            "INSERT INTO profiles (user_id, display_name, headline, location, bio) VALUES (?, ?, ?, ?, ?)",
            (user["id"], display_name, headline, location, bio),
        )
    return jsonify({"id": profile_id})


@bp.get("/dashboard")
@login_required
def dashboard(user):
    my_profile_row = db.fetchone("SELECT * FROM profiles WHERE user_id = ?", (user["id"],))
    profile_count = db.fetchone("SELECT COUNT(*) AS total FROM profiles")["total"]
    reflection_count = db.fetchone(
        "SELECT COUNT(*) AS total FROM reflections WHERE user_id = ?", (user["id"],)
    )["total"]
    recent_profiles = db.fetchall(
        """SELECT profiles.*, users.full_name
           FROM profiles JOIN users ON users.id = profiles.user_id
           ORDER BY profiles.id DESC LIMIT 6"""
    )
    for row in recent_profiles:
        row["is_owner"] = row["user_id"] == user["id"]

    return jsonify(
        {
            "user": user,
            "profile": my_profile_row,
            "profile_count": profile_count,
            "reflection_count": reflection_count,
            "recent_profiles": recent_profiles,
        }
    )

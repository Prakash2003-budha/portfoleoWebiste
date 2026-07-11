from flask import Blueprint, jsonify, request

from auth import current_user, login_required
from models import ProfileModel, ReflectionModel

bp = Blueprint("profiles", __name__, url_prefix="/api")


@bp.get("/profiles")
def list_profiles():
    user = current_user()
    rows = ProfileModel.list_public()
    for row in rows:
        row["is_owner"] = bool(user) and row["user_id"] == user["id"]
    return jsonify(rows)


@bp.get("/profiles/<int:profile_id>")
def get_profile(profile_id):
    row = ProfileModel.get_by_id(profile_id)
    if not row:
        return jsonify({"error": "Profile not found."}), 404
    user = current_user()
    row["is_owner"] = bool(user) and row["user_id"] == user["id"]
    return jsonify(row)


@bp.get("/profile/me")
@login_required
def my_profile(user):
    row = ProfileModel.get_by_user_id(user["id"])
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

    profile_id = ProfileModel.upsert_for_user(user["id"], display_name, headline, location, bio)
    return jsonify({"id": profile_id})


@bp.get("/dashboard")
@login_required
def dashboard(user):
    my_profile_row = ProfileModel.get_by_user_id(user["id"])
    profile_count = ProfileModel.count_all()
    reflection_count = ReflectionModel.count_for_user(user["id"])
    recent_profiles = ProfileModel.list_recent(6)
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

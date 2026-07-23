from flask import Blueprint, jsonify, request

import cloudinary_service
from auth import current_user, login_required
from models import ProfileModel, ReflectionModel

bp = Blueprint("profiles", __name__, url_prefix="/api")

ALLOWED_AVATAR_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_AVATAR_BYTES = 5 * 1024 * 1024  # 5MB


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


@bp.post("/profile/me/avatar")
@login_required
def upload_avatar(user):
    if not cloudinary_service.is_configured():
        return jsonify({
            "error": "Photo uploads aren't set up yet. Add CLOUDINARY_CLOUD_NAME, "
                     "CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET to backend/.env."
        }), 503

    file = request.files.get("avatar")
    if not file or not file.filename:
        return jsonify({"error": "Choose an image to upload."}), 400

    if file.mimetype not in ALLOWED_AVATAR_TYPES:
        return jsonify({"error": "Please upload a PNG, JPG, WEBP, or GIF image."}), 400

    file.seek(0, 2)  # seek to end to measure size
    size = file.tell()
    file.seek(0)
    if size > MAX_AVATAR_BYTES:
        return jsonify({"error": "That image is too large. Please keep it under 5MB."}), 413

    try:
        secure_url, public_id = cloudinary_service.upload_avatar(file, user["id"])
    except Exception as exc:  # pragma: no cover - network/service errors
        return jsonify({"error": f"Upload failed: {exc}"}), 502

    profile = ProfileModel.set_avatar(user["id"], secure_url, public_id)
    return jsonify({"avatar_url": secure_url, "profile": profile})


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

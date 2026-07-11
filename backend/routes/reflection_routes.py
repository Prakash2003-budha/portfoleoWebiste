from flask import Blueprint, jsonify, request

from auth import login_required
from models import FeedbackModel, ReflectionModel

bp = Blueprint("reflections", __name__, url_prefix="/api")


@bp.get("/reflections")
@login_required
def list_reflections(user):
    rows = ReflectionModel.list_for_user(user["id"])
    return jsonify(rows)


@bp.post("/reflections")
@login_required
def add_reflection(user):
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    body = (data.get("body") or "").strip()
    mood = (data.get("mood") or "").strip()
    if not title or not body:
        return jsonify({"error": "Title and entry text are required."}), 400
    new_id = ReflectionModel.create(user["id"], title, body, mood)
    return jsonify({"id": new_id}), 201


@bp.post("/feedback")
def add_feedback():
    """Usability feedback form for evaluation participants (Objective 4 of the
    proposal). Intentionally open, no login required, since testers may not
    have an account."""
    data = request.get_json(silent=True) or {}
    visitor_name = (data.get("visitor_name") or "Anonymous").strip()
    try:
        clarity_rating = int(data.get("clarity_rating"))
        identity_rating = int(data.get("identity_rating"))
    except (TypeError, ValueError):
        return jsonify({"error": "Ratings must be numbers between 1 and 5."}), 400
    if not (1 <= clarity_rating <= 5 and 1 <= identity_rating <= 5):
        return jsonify({"error": "Ratings must be between 1 and 5."}), 400
    comments = (data.get("comments") or "").strip()

    new_id = FeedbackModel.create(visitor_name, clarity_rating, identity_rating, comments)
    return jsonify({"id": new_id}), 201

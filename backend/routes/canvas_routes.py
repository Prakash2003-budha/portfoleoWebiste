import json

from flask import Blueprint, jsonify, request

from auth import login_required
from models import CanvasModel, ProfileModel

bp = Blueprint("canvas", __name__, url_prefix="/api/canvas")

MAX_ELEMENTS = 300
MAX_PAYLOAD_CHARS = 15_000_000  # generous headroom for a handful of base64 photos
MIN_CANVAS = 200
MAX_CANVAS = 4000


def _serialize(row):
    if not row:
        return None
    return {
        "canvas_width": row["canvas_width"],
        "canvas_height": row["canvas_height"],
        "background_color": row["background_color"],
        "elements": json.loads(row["elements"] or "[]"),
        "updated_at": row["updated_at"],
    }


def _default_layout():
    return {
        "canvas_width": CanvasModel.DEFAULT_WIDTH,
        "canvas_height": CanvasModel.DEFAULT_HEIGHT,
        "background_color": CanvasModel.DEFAULT_BACKGROUND,
        "elements": [],
        "updated_at": None,
    }


@bp.get("/me")
@login_required
def get_my_canvas(user):
    row = CanvasModel.get_by_user(user["id"])
    return jsonify(_serialize(row) or _default_layout())


@bp.get("/user/<int:user_id>")
def get_user_canvas(user_id):
    owner = ProfileModel.get_by_user_id(user_id)
    if not owner:
        return jsonify({"error": "No canvas for that user."}), 404
    row = CanvasModel.get_by_user(user_id)
    return jsonify(_serialize(row) or _default_layout())


@bp.put("/me")
@login_required
def save_my_canvas(user):
    data = request.get_json(silent=True) or {}
    elements = data.get("elements")
    canvas_width = data.get("canvas_width", CanvasModel.DEFAULT_WIDTH)
    canvas_height = data.get("canvas_height", CanvasModel.DEFAULT_HEIGHT)
    background_color = data.get("background_color", CanvasModel.DEFAULT_BACKGROUND)

    if not isinstance(elements, list):
        return jsonify({"error": "elements must be a list."}), 400
    if len(elements) > MAX_ELEMENTS:
        return jsonify({"error": f"Too many elements (max {MAX_ELEMENTS})."}), 400
    try:
        canvas_width = int(canvas_width)
        canvas_height = int(canvas_height)
    except (TypeError, ValueError):
        return jsonify({"error": "canvas_width/canvas_height must be numbers."}), 400
    if not (MIN_CANVAS <= canvas_width <= MAX_CANVAS) or not (MIN_CANVAS <= canvas_height <= MAX_CANVAS):
        return jsonify({"error": f"Canvas size must be between {MIN_CANVAS} and {MAX_CANVAS}px."}), 400
    if not isinstance(background_color, str) or not background_color:
        background_color = CanvasModel.DEFAULT_BACKGROUND

    elements_json = json.dumps(elements)
    if len(elements_json) > MAX_PAYLOAD_CHARS:
        return jsonify({"error": "Layout is too large — try smaller/fewer photos."}), 413

    CanvasModel.upsert(user["id"], canvas_width, canvas_height, background_color, elements_json)
    return jsonify({"ok": True})

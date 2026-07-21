from flask import Blueprint, jsonify, request

from auth import current_user, login_required
from models import PostModel

bp = Blueprint("posts", __name__, url_prefix="/api/posts")

MAX_TITLE_LEN = 120
# ~6MB raw, generous enough for a canvas thumbnail + json but keeps someone
# from wedging a giant video/file in through the JSON body.
MAX_PAYLOAD_LEN = 6_000_000


def _serialize(row, viewer):
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "title": row["title"],
        "thumbnail": row["thumbnail"],
        "width": row.get("width"),
        "height": row.get("height"),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "display_name": row.get("display_name") or row.get("full_name"),
        "is_owner": bool(viewer) and viewer["id"] == row["user_id"],
    }


@bp.get("")
def list_public_posts():
    viewer = current_user()
    rows = PostModel.list_public()
    return jsonify([_serialize(row, viewer) for row in rows])


@bp.get("/user/<int:user_id>")
def list_user_posts(user_id):
    viewer = current_user()
    rows = PostModel.list_for_user(user_id)
    return jsonify([_serialize(row, viewer) for row in rows])


@bp.get("/<int:post_id>")
def get_post(post_id):
    row = PostModel.get_by_id(post_id)
    if not row:
        return jsonify({"error": "Post not found."}), 404
    viewer = current_user()
    data = _serialize(row, viewer)
    # Only ship the editable canvas JSON to the owner (viewers just need
    # the thumbnail); keeps the read-only feed payload small.
    if data["is_owner"]:
        data["canvas_json"] = row["canvas_json"]
    return jsonify(data)


@bp.post("")
@login_required
def create_post(user):
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled post").strip()[:MAX_TITLE_LEN]
    canvas_json = data.get("canvas_json")
    thumbnail = data.get("thumbnail")
    width = data.get("width") or 1080
    height = data.get("height") or 1080

    if not canvas_json or not thumbnail:
        return jsonify({"error": "The canvas is empty — add something before saving."}), 400
    if len(str(canvas_json)) + len(str(thumbnail)) > MAX_PAYLOAD_LEN:
        return jsonify({"error": "This post is too large to save. Try removing a large image."}), 413

    new_id = PostModel.create(user["id"], title, canvas_json, thumbnail, width, height)
    return jsonify({"id": new_id}), 201


@bp.put("/<int:post_id>")
@login_required
def update_post(user, post_id):
    row = PostModel.get_by_id(post_id)
    if not row or row["user_id"] != user["id"]:
        return jsonify({"error": "Not found."}), 404

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled post").strip()[:MAX_TITLE_LEN]
    canvas_json = data.get("canvas_json")
    thumbnail = data.get("thumbnail")
    width = data.get("width") or row.get("width") or 1080
    height = data.get("height") or row.get("height") or 1080

    if not canvas_json or not thumbnail:
        return jsonify({"error": "The canvas is empty — add something before saving."}), 400
    if len(str(canvas_json)) + len(str(thumbnail)) > MAX_PAYLOAD_LEN:
        return jsonify({"error": "This post is too large to save. Try removing a large image."}), 413

    PostModel.update(post_id, title, canvas_json, thumbnail, width, height)
    return jsonify({"ok": True})


@bp.delete("/<int:post_id>")
@login_required
def delete_post(user, post_id):
    row = PostModel.get_by_id(post_id)
    if not row or row["user_id"] != user["id"]:
        return jsonify({"error": "Not found."}), 404
    PostModel.delete(post_id)
    return jsonify({"ok": True})

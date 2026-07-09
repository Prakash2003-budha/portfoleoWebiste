from flask import Blueprint, jsonify, request

from auth import login_required
from database import db

bp = Blueprint("portfolio", __name__, url_prefix="/api/portfolio")

# Section name -> (table, editable columns). Keeping "conventional" evidence
# (education/experiences/skills/achievements) and "identity" evidence
# (identity_traits/habits) in the same shape, per the project's whole point.
SECTIONS = {
    "education": ("education", ["institution", "qualification", "start_year", "end_year"]),
    "experiences": ("experiences", ["title", "organization", "description", "start_date", "end_date"]),
    "skills": ("skills", ["name", "category", "confidence_level"]),
    "achievements": ("achievements", ["title", "description", "achieved_on"]),
    "identity_traits": ("identity_traits", ["trait_name", "trait_type", "description", "visibility"]),
    "habits": ("habits", ["name", "frequency", "identity_link"]),
}


def _all_sections_for(user_id):
    result = {}
    for section, (table, _columns) in SECTIONS.items():
        result[section] = db.fetchall(
            f"SELECT * FROM {table} WHERE user_id = ? ORDER BY id DESC", (user_id,)
        )
    return result


@bp.get("/user/<int:user_id>")
def portfolio_for_user(user_id):
    owner = db.fetchone(
        """SELECT profiles.*, users.full_name FROM profiles
           JOIN users ON users.id = profiles.user_id WHERE profiles.user_id = ?""",
        (user_id,),
    )
    if not owner:
        return jsonify({"error": "No portfolio for that user."}), 404
    return jsonify({"owner": owner, "sections": _all_sections_for(user_id)})


@bp.get("/me")
@login_required
def portfolio_mine(user):
    return jsonify({"sections": _all_sections_for(user["id"])})


@bp.post("/<section>")
@login_required
def add_item(user, section):
    if section not in SECTIONS:
        return jsonify({"error": "Unknown portfolio section."}), 404
    table, columns = SECTIONS[section]
    data = request.get_json(silent=True) or {}
    values = [data.get(col) for col in columns]

    if not values[0]:
        return jsonify({"error": f"The first field of {section} is required."}), 400

    placeholders = ", ".join(["?"] * (len(columns) + 1))
    column_list = ", ".join(["user_id"] + columns)
    new_id = db.execute(
        f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})",
        tuple([user["id"]] + values),
    )
    return jsonify({"id": new_id}), 201


@bp.delete("/<section>/<int:item_id>")
@login_required
def delete_item(user, section, item_id):
    if section not in SECTIONS:
        return jsonify({"error": "Unknown portfolio section."}), 404
    table, _columns = SECTIONS[section]
    row = db.fetchone(f"SELECT user_id FROM {table} WHERE id = ?", (item_id,))
    if not row or row["user_id"] != user["id"]:
        return jsonify({"error": "Not found."}), 404
    db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
    return jsonify({"ok": True})

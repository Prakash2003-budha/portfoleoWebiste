from flask import Blueprint, jsonify, request

from auth import login_required
from models import PortfolioModel

bp = Blueprint("portfolio", __name__, url_prefix="/api/portfolio")


def _all_sections_for(user_id):
    result = {}
    for section, cfg in PortfolioModel.SECTIONS.items():
        result[section] = PortfolioModel.list_section(section, user_id)
    return result


@bp.get("/schema")
def get_portfolio_schema():
    return jsonify(PortfolioModel.get_schema())


@bp.get("/user/<int:user_id>")
def portfolio_for_user(user_id):
    owner = PortfolioModel.owner_profile(user_id)
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
    if section not in PortfolioModel.SECTIONS:
        return jsonify({"error": "Unknown portfolio section."}), 404
    table, columns = PortfolioModel.SECTIONS[section]
    data = request.get_json(silent=True) or {}
    values = [data.get(col) for col in columns]

    if not values[0]:
        return jsonify({"error": f"The first field of {section} is required."}), 400

    new_id = PortfolioModel.add_item(table, user["id"], columns, values)
    return jsonify({"id": new_id}), 201


@bp.delete("/<section>/<int:item_id>")
@login_required
def delete_item(user, section, item_id):
    if section not in PortfolioModel.SECTIONS:
        return jsonify({"error": "Unknown portfolio section."}), 404
    table = section
    row = PortfolioModel.get_owner_id(table, item_id)
    if not row or row["user_id"] != user["id"]:
        return jsonify({"error": "Not found."}), 404
    PortfolioModel.delete_item(table, item_id)
    return jsonify({"ok": True})

from flask import Blueprint, jsonify, make_response, request

from auth import SESSION_COOKIE, create_session, current_user, destroy_session, login_required
from database import db
from security import make_password_hash, verify_password

bp = Blueprint("auth", __name__, url_prefix="/api")


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not full_name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400
    if db.fetchone("SELECT id FROM users WHERE lower(email) = lower(?)", (email,)):
        return jsonify({"error": "That email is already registered."}), 409

    user_id = db.execute(
        "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
        (full_name, email, make_password_hash(password)),
    )
    # Every new account starts with a draft profile, same as the original prototype.
    db.execute(
        "INSERT INTO profiles (user_id, display_name, headline, location, bio) VALUES (?, ?, ?, ?, ?)",
        (user_id, full_name, "New member building a full-person portfolio", "", ""),
    )

    token = create_session(user_id)
    resp = make_response(jsonify({"id": user_id, "full_name": full_name, "email": email}))
    resp.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="Lax")
    return resp, 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    user = db.fetchone("SELECT * FROM users WHERE lower(email) = lower(?)", (email,))
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_session(user["id"])
    resp = make_response(
        jsonify({"id": user["id"], "full_name": user["full_name"], "email": user["email"]})
    )
    resp.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="Lax")
    return resp


@bp.post("/logout")
def logout():
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        destroy_session(token)
    resp = make_response(jsonify({"ok": True}))
    resp.delete_cookie(SESSION_COOKIE)
    return resp


@bp.get("/me")
def me():
    user = current_user()
    if not user:
        return jsonify({"error": "Not signed in."}), 401
    return jsonify(user)

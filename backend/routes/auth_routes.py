from flask import Blueprint, jsonify, make_response, request

from auth import SESSION_COOKIE, create_session, current_user, destroy_session, login_required
from mailer import send_activation_email
from models import ProfileModel, UserModel
from security import make_password_hash, verify_password, new_activation_code

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

    existing = UserModel.find_by_email(email)
    if existing:
        if existing["activated"]:
            return jsonify({"error": "That email is already registered. Try logging in instead."}), 409

        # Registered before but never activated (e.g. they closed the tab,
        # lost the email, or the previous attempt failed). Reissue a fresh
        # code instead of dead-ending them with a plain error.
        activation_code = new_activation_code()
        UserModel.resend_activation(existing["id"], activation_code)

        sent = send_activation_email(email, existing["full_name"], activation_code)
        if not sent:
            return (
                jsonify(
                    {
                        "error": "We couldn't resend the activation email. Check SMTP settings and try again.",
                    }
                ),
                500,
            )

        return jsonify(
            {
                "id": existing["id"],
                "pending_activation": True,
                "message": "That email was already registered but not activated yet. We've sent a fresh code — check your inbox.",
            }
        ), 200

    activation_code = new_activation_code()
    user_id = UserModel.create(full_name, email, make_password_hash(password), activation_code)
    ProfileModel.upsert_for_user(
        user_id,
        full_name,
        "New member building a full-person portfolio",
        "",
        "",
    )

    sent = send_activation_email(email, full_name, activation_code)
    if not sent:
        return (
            jsonify(
                {
                    "error": "Registration saved, but activation email could not be delivered. Check SMTP settings.",
                }
            ),
            500,
        )

    return jsonify(
        {
            "id": user_id,
            "pending_activation": True,
            "message": "Registration successful. Check your email for a one-time activation code.",
        }
    ), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    user = UserModel.find_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password."}), 401
    if not user.get("activated"):
        return jsonify({"error": "Account not activated. Please check your email."}), 403

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


@bp.post("/activate")
def activate():
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    if not code:
        return jsonify({"error": "Activation code is required."}), 400

    updated = UserModel.activate(code)
    if not updated:
        return jsonify({"error": "Invalid activation code."}), 400
    return jsonify({"ok": True, "message": "Account activated. You can now log in."})


@bp.route("/activate/<token>", methods=["GET"])
def activate_link(token):
    updated = UserModel.activate(token)
    if not updated:
        return jsonify({"error": "Invalid or expired activation code."}), 400
    return jsonify({"ok": True, "message": "Account activated. You can now log in."})
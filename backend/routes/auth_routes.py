from flask import Blueprint, jsonify, make_response, request

from auth import SESSION_COOKIE, create_session, current_user, destroy_session
from config import Config
from datetime import datetime, timedelta
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
        # Enforce resend cooldown
        last_sent = existing.get("activation_sent_at") or existing.get("activation_sent_at")
        if last_sent:
            try:
                last = datetime.strptime(last_sent, "%Y-%m-%d %H:%M:%S")
            except Exception:
                try:
                    last = datetime.fromisoformat(last_sent)
                except Exception:
                    last = None

            if last:
                elapsed = datetime.utcnow() - last
                if elapsed.total_seconds() < Config.ACTIVATION_RESEND_SECONDS:
                    wait = int(Config.ACTIVATION_RESEND_SECONDS - elapsed.total_seconds())
                    return (
                        jsonify(
                            {
                                "error": f"Please wait {wait} seconds before requesting another activation code.",
                                "pending_activation": True,
                                "retry_after": wait,
                            }
                        ),
                        429,
                    )

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
                "message": "That email was already registered but not activated yet. We've sent a fresh code -- check your inbox.",
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
        return (
            jsonify(
                {
                    "error": "Account not activated. Check your email for the one-time activation code.",
                    "pending_activation": True,
                }
            ),
            403,
        )

    token = create_session(user["id"])
    resp = make_response(
        jsonify({"id": user["id"], "full_name": user["full_name"], "email": user["email"]})
    )
    resp.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite="Lax",
        secure=Config.COOKIE_SECURE,
        max_age=30 * 24 * 60 * 60,  # 30 days
    )
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


@bp.post("/resend-activation")
def resend_activation():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email is required."}), 400

    existing = UserModel.find_by_email(email)
    if not existing:
        return jsonify({"error": "No account found with that email."}), 404
    if existing.get("activated"):
        return jsonify({"error": "Account already activated."}), 400

    # Enforce resend cooldown
    last_sent = existing.get("activation_sent_at")
    if last_sent:
        try:
            last = datetime.strptime(last_sent, "%Y-%m-%d %H:%M:%S")
        except Exception:
            try:
                last = datetime.fromisoformat(last_sent)
            except Exception:
                last = None

        if last:
            elapsed = datetime.utcnow() - last
            if elapsed.total_seconds() < Config.ACTIVATION_RESEND_SECONDS:
                wait = int(Config.ACTIVATION_RESEND_SECONDS - elapsed.total_seconds())
                return (
                    jsonify({"error": "Too many requests", "pending_activation": True, "retry_after": wait}),
                    429,
                )

    activation_code = new_activation_code()
    UserModel.resend_activation(existing["id"], activation_code)

    sent = send_activation_email(email, existing["full_name"], activation_code)
    if not sent:
        return (
            jsonify({"error": "We couldn't resend the activation email. Check SMTP settings and try again."}),
            500,
        )

    return jsonify({"ok": True, "pending_activation": True, "message": "Activation code sent.", "retry_after": Config.ACTIVATION_RESEND_SECONDS}), 200


@bp.get("/activation-status")
def activation_status():
    email = (request.args.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email is required."}), 400

    existing = UserModel.find_by_email(email)
    if not existing:
        return jsonify({"error": "No account found with that email."}), 404

    if existing.get("activated"):
        return jsonify({"activated": True, "can_resend": False, "retry_after": 0}), 200

    last_sent = existing.get("activation_sent_at")
    if not last_sent:
        return jsonify({"activated": False, "can_resend": True, "retry_after": 0}), 200

    try:
        last = datetime.strptime(last_sent, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            last = datetime.fromisoformat(last_sent)
        except Exception:
            last = None

    if not last:
        return jsonify({"activated": False, "can_resend": True, "retry_after": 0}), 200

    elapsed = datetime.utcnow() - last
    remaining = int(max(0, Config.ACTIVATION_RESEND_SECONDS - elapsed.total_seconds()))
    return jsonify({"activated": False, "can_resend": remaining == 0, "retry_after": remaining}), 200
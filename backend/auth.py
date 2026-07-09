"""
auth.py
-------
Very small in-memory session store, mirroring the cookie-based session
approach from the original prototype (no external session/JWT library,
so it stays easy to explain in a viva).
"""

from functools import wraps

from flask import jsonify, request

from database import db
from security import new_session_token

SESSION_COOKIE = "pfw_session"

# session_token -> user_id
sessions = {}


def create_session(user_id):
    token = new_session_token()
    sessions[token] = user_id
    return token


def destroy_session(token):
    sessions.pop(token, None)


def current_user():
    token = request.cookies.get(SESSION_COOKIE)
    user_id = sessions.get(token)
    if not user_id:
        return None
    return db.fetchone(
        "SELECT id, email, full_name, role FROM users WHERE id = ?", (user_id,)
    )


def login_required(view_func):
    """Decorator for routes that need an authenticated user.

    Injects the current user as the first positional argument.
    """

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"error": "Login required."}), 401
        return view_func(user, *args, **kwargs)

    return wrapped

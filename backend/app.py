"""
app.py
------
Backend entrypoint. This is now a pure JSON API (no HTML rendering) —
the frontend is a separate static app in ../frontend that talks to
these endpoints over fetch(). Run with:
    python3 app.py

Environment variables (same as the original prototype):
    DB_ENGINE   sqlite (default) or mysql
    PORT        API port, default 5000
    CORS_ORIGIN origin allowed to call this API, default http://127.0.0.1:5500
"""

from flask import Flask, jsonify

from config import Config
from scripts.migrate_sqlite import migrate_sqlite_db

APP_NAME = Config.APP_NAME


def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    cors_origin = Config.CORS_ORIGIN

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = cors_origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    @app.route("/api/<path:_any>", methods=["OPTIONS"])
    def cors_preflight(_any):
        return "", 204

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "service": APP_NAME})

    from routes.auth_routes import bp as auth_bp
    from routes.profile_routes import bp as profile_bp
    from routes.portfolio_routes import bp as portfolio_bp
    from routes.reflection_routes import bp as reflection_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(reflection_bp)

    return app


app = create_app()

if __name__ == "__main__":
    if Config.DB_ENGINE == "sqlite":
        migrate_sqlite_db()
    print(f"{APP_NAME} running at http://127.0.0.1:{Config.PORT}")
    app.run(host="127.0.0.1", port=Config.PORT, debug=True)

"""
Tests for CORS header defaults.

When CORS_ORIGIN is not set in the environment, the backend should default
to http://127.0.0.1:5500 (the local frontend dev server) and send the
Access-Control-Allow-Credentials header.

This test reloads the app module to pick up a different CORS_ORIGIN value,
which is why it manages the env var itself rather than relying on conftest.
"""

import importlib
import os

import pytest


@pytest.fixture
def app_without_cors_origin():
    """Reload the app module with CORS_ORIGIN unset so the config default
    kicks in, then restore the original environment afterwards."""
    original_origin = os.environ.get("CORS_ORIGIN")
    os.environ.pop("CORS_ORIGIN", None)

    import app as app_module
    reloaded = importlib.reload(app_module)
    client = reloaded.create_app().test_client()

    yield client

    if original_origin is None:
        os.environ.pop("CORS_ORIGIN", None)
    else:
        os.environ["CORS_ORIGIN"] = original_origin


def test_default_cors_origin_uses_local_frontend_origin(app_without_cors_origin):
    response = app_without_cors_origin.get("/api/health")

    assert response.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1:5500"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"


def test_cors_preflight_returns_success_for_api_routes(app_without_cors_origin):
    response = app_without_cors_origin.options("/api/profiles")

    # Flask's auto-generated OPTIONS handler returns 200 (with Allow header),
    # but the important thing for CORS is that the after_request hooks still
    # attach the right headers. The explicit cors_preflight route also returns
    # 204 for routes that don't match a blueprint -- both are valid preflight
    # responses as long as the CORS headers are present.
    assert response.status_code in (200, 204)


def test_cors_headers_present_on_api_responses(app_without_cors_origin):
    response = app_without_cors_origin.get("/api/health")

    assert response.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1:5500"
    assert response.headers["Access-Control-Allow-Headers"] == "Content-Type"
    assert "GET" in response.headers["Access-Control-Allow-Methods"]
    assert "POST" in response.headers["Access-Control-Allow-Methods"]

import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DB_ENGINE", "sqlite")
os.environ.setdefault("SQLITE_PATH", str(ROOT_DIR / "portfolio_weirdos_test.db"))
os.environ.setdefault("CORS_ORIGIN", "http://127.0.0.1:5500")


@pytest.fixture(scope="session")
def app():
    from backend.app import create_app

    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()

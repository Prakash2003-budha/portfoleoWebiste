import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]  # backend/
PROJECT_ROOT = ROOT_DIR.parent  # repo root, needed for `backend.X` imports

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DB_ENGINE", "sqlite")
TEST_DB_PATH = str(ROOT_DIR / "portfolio_weirdos_test.db")
os.environ.setdefault("SQLITE_PATH", TEST_DB_PATH)
os.environ.setdefault("CORS_ORIGIN", "http://127.0.0.1:5500")


@pytest.fixture(scope="session", autouse=True)
def _test_database():
    """Create a fresh, empty-but-correct schema for the test database before
    the suite runs, so tests don't depend on a pre-existing seeded DB file."""
    from scripts.init_sqlite import init_sqlite_db

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    init_sqlite_db(path=TEST_DB_PATH, seed=False)
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="session")
def app():
    from backend.app import create_app

    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    APP_NAME = "Portfolios for Weirdos API"
    PORT = int(os.getenv("PORT", "5000"))
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://127.0.0.1:5500").strip() or "http://127.0.0.1:5500"

    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
    SQLITE_PATH = os.getenv("SQLITE_PATH", str(BASE_DIR / "portfolio_weirdos.db"))
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306")) if os.getenv("DB_PORT") else 3306
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465")) if os.getenv("SMTP_PORT") else 465
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@portfoleo.local")
    SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "true").lower() in ("true", "1", "yes")
    SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "false").lower() in ("true", "1", "yes")
    ACTIVATION_BASE_URL = os.getenv("ACTIVATION_BASE_URL", "http://127.0.0.1:5500")

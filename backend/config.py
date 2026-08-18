import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    APP_NAME = "Portfolios for Weirdos API"
    PORT = int(os.getenv("PORT", "5000"))
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://127.0.0.1:5500").strip() or "http://127.0.0.1:5500"
    COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")

    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
    SQLITE_PATH = os.getenv("SQLITE_PATH", str(BASE_DIR / "portfolio_weirdos.db"))

    SMTP_PROVIDER = os.getenv("SMTP_PROVIDER", "")
    SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465")) if os.getenv("SMTP_PORT") else 465
    SMTP_USER = os.getenv("SMTP_USER", "").strip()
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip().strip('"').strip("'")
    SMTP_FROM = os.getenv("SMTP_FROM", os.getenv("SMTP_PROVIDER", "no-reply@portfoleo.local")).strip()
    SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "true").lower() in ("true", "1", "yes")
    SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "false").lower() in ("true", "1", "yes")
    ACTIVATION_BASE_URL = os.getenv("ACTIVATION_BASE_URL", "http://127.0.0.1:5500").strip()

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "").strip()
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "").strip()
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "").strip()

    @classmethod
    def cloudinary_configured(cls):
        return bool(cls.CLOUDINARY_CLOUD_NAME and cls.CLOUDINARY_API_KEY and cls.CLOUDINARY_API_SECRET)

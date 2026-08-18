import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    if load_dotenv:
        load_dotenv(ENV_PATH)
    else:
        with ENV_PATH.open() as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key:
                    os.environ.setdefault(key, value)


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

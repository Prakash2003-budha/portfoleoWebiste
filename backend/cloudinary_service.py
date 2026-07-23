"""
cloudinary_service.py
----------------------
Thin wrapper around the Cloudinary SDK, used for one thing right now:
uploading a user's profile picture so everyone browsing the directory can
see a real photo instead of a two-letter initials badge.

Cloudinary is configured from environment variables (see backend/.env):
    CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET

If those aren't set, `is_configured()` returns False and the route that
calls this module returns a clear error instead of crashing.
"""

import cloudinary
import cloudinary.uploader

from config import Config

_configured = False


def _ensure_configured():
    global _configured
    if _configured:
        return
    cloudinary.config(
        cloud_name=Config.CLOUDINARY_CLOUD_NAME,
        api_key=Config.CLOUDINARY_API_KEY,
        api_secret=Config.CLOUDINARY_API_SECRET,
        secure=True,
    )
    _configured = True


def is_configured():
    return Config.cloudinary_configured()


def upload_avatar(file_storage, user_id):
    """Upload a Flask `FileStorage` (from request.files) to Cloudinary.

    Stores every user's avatar under a stable public_id
    (portfolio-weirdos/avatars/user_<id>) so re-uploading replaces the old
    photo instead of piling up unused images, and crops/resizes it down to
    a clean square so it's ready to use as an avatar everywhere.

    Returns (secure_url, public_id).
    """
    _ensure_configured()
    result = cloudinary.uploader.upload(
        file_storage,
        folder="portfolio-weirdos/avatars",
        public_id=f"user_{user_id}",
        overwrite=True,
        invalidate=True,
        resource_type="image",
        transformation=[
            {"width": 512, "height": 512, "crop": "fill", "gravity": "face"},
            {"quality": "auto", "fetch_format": "auto"},
        ],
    )
    return result.get("secure_url"), result.get("public_id")


def delete_avatar(public_id):
    if not public_id:
        return
    _ensure_configured()
    cloudinary.uploader.destroy(public_id, resource_type="image")

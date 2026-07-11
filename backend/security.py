"""
security.py
------------
Password hashing helpers (PBKDF2-SHA256, same scheme as the original
prototype so existing seeded password hashes keep working).
"""

import hashlib
import secrets


def make_password_hash(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def verify_password(password, stored_hash):
    try:
        algorithm, salt_hex, digest_hex = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200000)
        return secrets.compare_digest(actual, expected)
    except ValueError:
        return False


def new_session_token():
    return secrets.token_urlsafe(32)


def new_activation_token():
    return secrets.token_urlsafe(32)

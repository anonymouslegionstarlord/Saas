import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

ITERATIONS = 210_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, expected = stored.split(":", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITERATIONS).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_token(user_id: int, tenant_id: int, minutes: int) -> str:
    payload = {"sub": str(user_id), "tenant_id": tenant_id, "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes)}
    return jwt.encode(payload, os.getenv("JWT_SECRET", "development-only-secret-change-me"), algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, os.getenv("JWT_SECRET", "development-only-secret-change-me"), algorithms=["HS256"])


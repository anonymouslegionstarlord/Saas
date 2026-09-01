import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 210_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    salt, expected = encoded.split("$", 1)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 210_000)
    return hmac.compare_digest(actual.hex(), expected)


def create_token(user_id: int, tenant_id: int) -> str:
    secret = os.getenv("JWT_SECRET", "development-only-change-me")
    minutes = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
    payload = {"sub": str(user_id), "tenant_id": tenant_id, "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes)}
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, os.getenv("JWT_SECRET", "development-only-change-me"), algorithms=["HS256"])


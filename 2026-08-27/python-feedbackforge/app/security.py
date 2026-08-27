import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
import jwt

def password_hash(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"{salt.hex()}:{digest.hex()}"

def password_matches(password: str, encoded: str) -> bool:
    try:
        salt, expected = encoded.split(":", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 310_000)
        return hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False

def make_token(user_id: int, tenant_id: int, secret: str, ttl: int) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user_id), "tid": tenant_id, "iat": now, "exp": now + timedelta(minutes=ttl)}, secret, algorithm="HS256")

def read_token(token: str, secret: str) -> dict:
    return jwt.decode(token, secret, algorithms=["HS256"])

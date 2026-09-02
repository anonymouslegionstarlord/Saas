import hashlib, hmac, os, secrets
from datetime import datetime, timedelta, timezone
import jwt

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    value = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 210_000)
    return salt + "$" + value.hex()

def verify_password(password: str, encoded: str) -> bool:
    salt, expected = encoded.split("$", 1)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 210_000)
    return hmac.compare_digest(actual.hex(), expected)

def create_token(user_id: int, tenant_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MINUTES", "480")))
    return jwt.encode({"sub": str(user_id), "tenant_id": tenant_id, "exp": expires}, os.getenv("JWT_SECRET", "development-only"), algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, os.getenv("JWT_SECRET", "development-only"), algorithms=["HS256"])


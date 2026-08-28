import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
import jwt

def hash_password(password):
    salt=os.urandom(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310_000)
    return salt.hex()+":"+digest.hex()

def verify_password(password,encoded):
    try:
        salt,expected=encoded.split(":",1)
        actual=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),310_000)
        return hmac.compare_digest(actual.hex(),expected)
    except (ValueError,TypeError):
        return False

def issue_token(user_id,workspace_id,secret,ttl):
    now=datetime.now(timezone.utc)
    return jwt.encode({"sub":str(user_id),"wid":workspace_id,"iat":now,"exp":now+timedelta(minutes=ttl)},secret,algorithm="HS256")

def decode_token(token,secret):
    return jwt.decode(token,secret,algorithms=["HS256"])

import hashlib, hmac, os, secrets
from datetime import datetime, timedelta, timezone
import jwt

ROUNDS=210_000
def hash_password(password:str)->str:
    salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,ROUNDS)
    return f"{salt.hex()}:{digest.hex()}"
def verify_password(password:str,stored:str)->bool:
    try:
        salt,wanted=stored.split(":",1); got=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),ROUNDS).hex()
        return hmac.compare_digest(got,wanted)
    except (ValueError,TypeError): return False
def issue_token(user_id:int,tenant_id:int)->str:
    payload={"sub":str(user_id),"tenant_id":tenant_id,"exp":datetime.now(timezone.utc)+timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MINUTES","480")))}
    return jwt.encode(payload,os.getenv("JWT_SECRET","development-only-secret-change-me"),algorithm="HS256")
def read_token(token:str)->dict:
    return jwt.decode(token,os.getenv("JWT_SECRET","development-only-secret-change-me"),algorithms=["HS256"])


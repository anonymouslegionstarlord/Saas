import hashlib,hmac,os,secrets
from datetime import datetime,timedelta,timezone
import jwt

def hash_password(password):
    salt=secrets.token_hex(16);digest=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),210_000)
    return salt+"$"+digest.hex()
def verify_password(password,encoded):
    salt,expected=encoded.split("$",1);actual=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),210_000)
    return hmac.compare_digest(actual.hex(),expected)
def create_token(user_id,tenant_id):
    exp=datetime.now(timezone.utc)+timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MINUTES","480")))
    return jwt.encode({"sub":str(user_id),"tenant_id":tenant_id,"exp":exp},os.getenv("JWT_SECRET","development-only"),algorithm="HS256")
def decode_token(token): return jwt.decode(token,os.getenv("JWT_SECRET","development-only"),algorithms=["HS256"])


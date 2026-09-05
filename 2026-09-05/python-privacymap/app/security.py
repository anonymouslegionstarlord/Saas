import hashlib,hmac,os,secrets
from datetime import datetime,timedelta,timezone
import jwt
def hash_password(password):
    salt=secrets.token_hex(16);value=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),210000);return salt+"$"+value.hex()
def verify_password(password,encoded):
    salt,expected=encoded.split("$",1);value=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),210000);return hmac.compare_digest(value.hex(),expected)
def token(user_id,tenant_id):
    exp=datetime.now(timezone.utc)+timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MINUTES","480")));return jwt.encode({"sub":str(user_id),"tenant_id":tenant_id,"exp":exp},os.getenv("JWT_SECRET","development-only"),algorithm="HS256")
def decode(value): return jwt.decode(value,os.getenv("JWT_SECRET","development-only"),algorithms=["HS256"])


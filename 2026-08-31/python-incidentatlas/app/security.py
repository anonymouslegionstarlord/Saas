import hashlib,hmac,os
from datetime import datetime,timedelta,timezone
import jwt
def hash_password(value):
    salt=os.urandom(16);digest=hashlib.pbkdf2_hmac("sha256",value.encode(),salt,310_000);return salt.hex()+":"+digest.hex()
def verify_password(value,encoded):
    try:
        salt,expected=encoded.split(":",1);actual=hashlib.pbkdf2_hmac("sha256",value.encode(),bytes.fromhex(salt),310_000);return hmac.compare_digest(actual.hex(),expected)
    except (ValueError,TypeError):return False
def issue_token(uid,wid,secret,ttl):
    now=datetime.now(timezone.utc);return jwt.encode({"sub":str(uid),"wid":wid,"iat":now,"exp":now+timedelta(minutes=ttl)},secret,algorithm="HS256")
def decode_token(token,secret):return jwt.decode(token,secret,algorithms=["HS256"])

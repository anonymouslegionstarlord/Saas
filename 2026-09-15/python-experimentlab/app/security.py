import hashlib,hmac,os,secrets
from datetime import datetime,timedelta,timezone
import jwt
ROUNDS=210000
def hash_password(p):
    s=secrets.token_bytes(16);d=hashlib.pbkdf2_hmac('sha256',p.encode(),s,ROUNDS);return f'{s.hex()}:{d.hex()}'
def verify_password(p,stored):
    try:s,w=stored.split(':',1);return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),ROUNDS).hex(),w)
    except (ValueError,TypeError):return False
def create_token(uid,tid):
    return jwt.encode({'sub':str(uid),'tenant_id':tid,'exp':datetime.now(timezone.utc)+timedelta(minutes=int(os.getenv('ACCESS_TOKEN_MINUTES','480')))},os.getenv('JWT_SECRET','development-only-secret-change-me'),algorithm='HS256')
def decode_token(t):return jwt.decode(t,os.getenv('JWT_SECRET','development-only-secret-change-me'),algorithms=['HS256'])


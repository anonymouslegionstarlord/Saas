import os,sqlite3
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import jwt
from fastapi import Depends,FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from pydantic import BaseModel,EmailStr,Field,model_validator
from .db import connect,init_db
from .security import create_token,decode_token,hash_password,verify_password

ROOT=Path(__file__).parent;bearer=HTTPBearer(auto_error=False)
@asynccontextmanager
async def lifespan(_): init_db();yield
app=FastAPI(title=os.getenv("APP_NAME","CertSentinel"),lifespan=lifespan)

class Register(BaseModel):
    name:str=Field(min_length=2,max_length=80);workspace:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr;password:str
class PersonIn(BaseModel):
    name:str=Field(min_length=2,max_length=100);email:EmailStr;department:str=Field(min_length=2,max_length=80)
class CredentialIn(BaseModel):
    certification:str=Field(min_length=2,max_length=140);issuer:str=Field(min_length=2,max_length=120);credential_code:str=Field(default="",max_length=100)
    issued_on:date;expires_on:date;notes:str=Field(default="",max_length=1000)
    @model_validator(mode="after")
    def dates(self):
        if self.expires_on<=self.issued_on: raise ValueError("expiry must be after issue date")
        return self

def current_user(c:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not c: raise HTTPException(401,"Authentication required")
    try:
        p=decode_token(c.credentials);return {"id":int(p["sub"]),"tenant_id":int(p["tenant_id"])}
    except (jwt.PyJWTError,KeyError,ValueError): raise HTTPException(401,"Invalid or expired token")

@app.get("/",response_class=HTMLResponse)
def home(): return (ROOT/"static"/"index.html").read_text()

@app.post("/api/auth/register",status_code=201)
def register(body:Register):
    try:
        with connect() as db:
            tid=db.execute("INSERT INTO tenants(name) VALUES(?)",(body.workspace.strip(),)).lastrowid
            uid=db.execute("INSERT INTO users(tenant_id,name,email,password_hash) VALUES(?,?,?,?)",(tid,body.name.strip(),body.email.lower(),hash_password(body.password))).lastrowid
        return {"token":create_token(uid,tid)}
    except sqlite3.IntegrityError: raise HTTPException(409,"Email already registered")

@app.post("/api/auth/login")
def login(body:Login):
    with connect() as db: row=db.execute("SELECT * FROM users WHERE email=?",(body.email.lower(),)).fetchone()
    if not row or not verify_password(body.password,row["password_hash"]): raise HTTPException(401,"Invalid credentials")
    return {"token":create_token(row["id"],row["tenant_id"])}

@app.get("/api/dashboard")
def dashboard(user=Depends(current_user)):
    with connect() as db:
        items=[dict(x) for x in db.execute("""SELECT c.*,p.name person_name,p.department,
        CAST(julianday(c.expires_on)-julianday(date('now')) AS INTEGER) days_left FROM credentials c
        JOIN people p ON p.id=c.person_id AND p.tenant_id=c.tenant_id WHERE c.tenant_id=? ORDER BY c.expires_on""",(user["tenant_id"],))]
        people=[dict(x) for x in db.execute("SELECT * FROM people WHERE tenant_id=? ORDER BY name",(user["tenant_id"],))]
    return {"credentials":items,"people":people,"summary":{"total":len(items),"expiring":sum(0<=x["days_left"]<=30 for x in items),"expired":sum(x["days_left"]<0 for x in items)}}

@app.post("/api/people",status_code=201)
def add_person(body:PersonIn,user=Depends(current_user)):
    try:
        with connect() as db:
            pid=db.execute("INSERT INTO people(tenant_id,name,email,department) VALUES(?,?,?,?)",(user["tenant_id"],body.name.strip(),body.email.lower(),body.department.strip())).lastrowid
        return {"id":pid}
    except sqlite3.IntegrityError: raise HTTPException(409,"Person already exists in this workspace")

@app.post("/api/people/{person_id}/credentials",status_code=201)
def add_credential(person_id:int,body:CredentialIn,user=Depends(current_user)):
    try:
        with connect() as db:
            person=db.execute("SELECT id FROM people WHERE id=? AND tenant_id=?",(person_id,user["tenant_id"])).fetchone()
            if not person: raise HTTPException(404,"Person not found")
            cid=db.execute("""INSERT INTO credentials(tenant_id,person_id,certification,issuer,credential_code,issued_on,expires_on,notes)
            VALUES(?,?,?,?,?,?,?,?)""",(user["tenant_id"],person_id,body.certification.strip(),body.issuer.strip(),body.credential_code.strip(),body.issued_on.isoformat(),body.expires_on.isoformat(),body.notes.strip())).lastrowid
        return {"id":cid,"status":"active"}
    except sqlite3.IntegrityError: raise HTTPException(409,"Certification already tracked for this person")

@app.patch("/api/credentials/{credential_id}")
def update_status(credential_id:int,status_value:str,user=Depends(current_user)):
    if status_value not in {"active","renewing","expired","waived"}: raise HTTPException(422,"Invalid status")
    with connect() as db:
        row=db.execute("SELECT id FROM credentials WHERE id=? AND tenant_id=?",(credential_id,user["tenant_id"])).fetchone()
        if not row: raise HTTPException(404,"Credential not found")
        db.execute("UPDATE credentials SET status=? WHERE id=? AND tenant_id=?",(status_value,credential_id,user["tenant_id"]))
    return {"status":status_value}


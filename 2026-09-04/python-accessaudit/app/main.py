import os,sqlite3
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import jwt
from fastapi import Depends,FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from pydantic import BaseModel,EmailStr,Field,field_validator
from .db import connect,init_db
from .security import create_token,decode_token,hash_password,verify_password
ROOT=Path(__file__).parent;bearer=HTTPBearer(auto_error=False)
@asynccontextmanager
async def lifespan(_): init_db();yield
app=FastAPI(title=os.getenv("APP_NAME","AccessAudit"),lifespan=lifespan)
class Register(BaseModel):
    name:str=Field(min_length=2,max_length=80);workspace:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr;password:str
class SystemIn(BaseModel):
    name:str=Field(min_length=2,max_length=100);owner:str=Field(min_length=2,max_length=100);risk:str
    @field_validator("risk")
    @classmethod
    def risk_value(cls,v):
        if v not in {"low","medium","high"}: raise ValueError("invalid risk")
        return v
class GrantIn(BaseModel):
    subject_email:EmailStr;role:str=Field(min_length=2,max_length=100);review_due:date
class DecisionIn(BaseModel):
    decision:str;justification:str=Field(min_length=3,max_length=1000)
    @field_validator("decision")
    @classmethod
    def decision_value(cls,v):
        if v not in {"retain","revoke"}: raise ValueError("invalid decision")
        return v
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
        systems=[dict(x) for x in db.execute("""SELECT s.*,COUNT(g.id) grant_count,SUM(CASE WHEN g.decision='pending' THEN 1 ELSE 0 END) pending FROM systems s LEFT JOIN grants g ON g.system_id=s.id AND g.tenant_id=s.tenant_id WHERE s.tenant_id=? GROUP BY s.id ORDER BY s.risk DESC,s.name""",(user["tenant_id"],))]
        grants=[dict(x) for x in db.execute("""SELECT g.*,s.name system_name,s.risk FROM grants g JOIN systems s ON s.id=g.system_id AND s.tenant_id=g.tenant_id WHERE g.tenant_id=? ORDER BY g.review_due""",(user["tenant_id"],))]
    return {"systems":systems,"grants":grants,"summary":{"pending":sum(g["decision"]=="pending" for g in grants),"overdue":sum(g["decision"]=="pending" and g["review_due"]<date.today().isoformat() for g in grants),"high_risk":sum(s["risk"]=="high" for s in systems)}}
@app.post("/api/systems",status_code=201)
def add_system(body:SystemIn,user=Depends(current_user)):
    try:
        with connect() as db: sid=db.execute("INSERT INTO systems(tenant_id,name,owner,risk) VALUES(?,?,?,?)",(user["tenant_id"],body.name.strip(),body.owner.strip(),body.risk)).lastrowid
        return {"id":sid}
    except sqlite3.IntegrityError: raise HTTPException(409,"System already exists")
@app.post("/api/systems/{system_id}/grants",status_code=201)
def add_grant(system_id:int,body:GrantIn,user=Depends(current_user)):
    try:
        with connect() as db:
            if not db.execute("SELECT id FROM systems WHERE id=? AND tenant_id=?",(system_id,user["tenant_id"])).fetchone(): raise HTTPException(404,"System not found")
            gid=db.execute("INSERT INTO grants(tenant_id,system_id,subject_email,role,review_due) VALUES(?,?,?,?,?)",(user["tenant_id"],system_id,body.subject_email.lower(),body.role.strip(),body.review_due.isoformat())).lastrowid
        return {"id":gid,"decision":"pending"}
    except sqlite3.IntegrityError: raise HTTPException(409,"Access grant already exists")
@app.patch("/api/grants/{grant_id}")
def decide(grant_id:int,body:DecisionIn,user=Depends(current_user)):
    with connect() as db:
        if not db.execute("SELECT id FROM grants WHERE id=? AND tenant_id=?",(grant_id,user["tenant_id"])).fetchone(): raise HTTPException(404,"Access grant not found")
        db.execute("UPDATE grants SET decision=?,justification=?,reviewed_at=CURRENT_TIMESTAMP WHERE id=? AND tenant_id=?",(body.decision,body.justification.strip(),grant_id,user["tenant_id"]))
    return {"decision":body.decision}


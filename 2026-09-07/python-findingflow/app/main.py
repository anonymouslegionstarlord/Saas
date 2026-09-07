import os,sqlite3
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import jwt
from fastapi import Depends,FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from pydantic import BaseModel,EmailStr,Field,field_validator,model_validator
from .db import connect,init_db
from .security import create_token,decode_token,hash_password,verify_password
ROOT=Path(__file__).parent;bearer=HTTPBearer(auto_error=False)
@asynccontextmanager
async def lifespan(_): init_db();yield
app=FastAPI(title=os.getenv("APP_NAME","FindingFlow"),lifespan=lifespan)
class Register(BaseModel): name:str=Field(min_length=2,max_length=80);workspace:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr;password:str
class AuditIn(BaseModel):
    title:str=Field(min_length=2,max_length=140);area:str=Field(min_length=2,max_length=100);lead:str=Field(min_length=2,max_length=100);starts_on:date;ends_on:date
    @model_validator(mode="after")
    def dates(self):
        if self.ends_on<self.starts_on: raise ValueError("end date must not precede start date")
        return self
class FindingIn(BaseModel):
    title:str=Field(min_length=3,max_length=180);severity:str;owner:str=Field(min_length=2,max_length=100);due_on:date
    @field_validator("severity")
    @classmethod
    def severity_value(cls,v):
        if v not in {"low","medium","high","critical"}: raise ValueError("invalid severity")
        return v
class FindingUpdate(BaseModel):
    status:str;remediation:str=Field(min_length=3,max_length=1500)
    @field_validator("status")
    @classmethod
    def status_value(cls,v):
        if v not in {"open","in_progress","verified","accepted"}: raise ValueError("invalid status")
        return v
def user(c:HTTPAuthorizationCredentials|None=Depends(bearer)):
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
            tid=db.execute("INSERT INTO tenants(name) VALUES(?)",(body.workspace.strip(),)).lastrowid;uid=db.execute("INSERT INTO users(tenant_id,name,email,password_hash) VALUES(?,?,?,?)",(tid,body.name.strip(),body.email.lower(),hash_password(body.password))).lastrowid
        return {"token":create_token(uid,tid)}
    except sqlite3.IntegrityError: raise HTTPException(409,"Email already registered")
@app.post("/api/auth/login")
def login(body:Login):
    with connect() as db: row=db.execute("SELECT * FROM users WHERE email=?",(body.email.lower(),)).fetchone()
    if not row or not verify_password(body.password,row["password_hash"]): raise HTTPException(401,"Invalid credentials")
    return {"token":create_token(row["id"],row["tenant_id"])}
@app.get("/api/dashboard")
def dashboard(current=Depends(user)):
    with connect() as db:
        audits=[dict(x) for x in db.execute("""SELECT a.*,COUNT(f.id) finding_count,SUM(CASE WHEN f.status='open' THEN 1 ELSE 0 END) open_findings FROM audits a LEFT JOIN findings f ON f.audit_id=a.id AND f.tenant_id=a.tenant_id WHERE a.tenant_id=? GROUP BY a.id ORDER BY a.ends_on""",(current["tenant_id"],))]
        findings=[dict(x) for x in db.execute("""SELECT f.*,a.title audit_title FROM findings f JOIN audits a ON a.id=f.audit_id AND a.tenant_id=f.tenant_id WHERE f.tenant_id=? ORDER BY f.due_on""",(current["tenant_id"],))]
    return {"audits":audits,"findings":findings,"summary":{"open":sum(f["status"]=="open" for f in findings),"critical":sum(f["severity"]=="critical" and f["status"]!="verified" for f in findings),"overdue":sum(f["due_on"]<date.today().isoformat() and f["status"] not in {"verified","accepted"} for f in findings)}}
@app.post("/api/audits",status_code=201)
def add_audit(body:AuditIn,current=Depends(user)):
    try:
        with connect() as db: aid=db.execute("INSERT INTO audits(tenant_id,title,area,lead,starts_on,ends_on) VALUES(?,?,?,?,?,?)",(current["tenant_id"],body.title.strip(),body.area.strip(),body.lead.strip(),body.starts_on.isoformat(),body.ends_on.isoformat())).lastrowid
        return {"id":aid,"status":"open"}
    except sqlite3.IntegrityError: raise HTTPException(409,"Audit already exists")
@app.post("/api/audits/{audit_id}/findings",status_code=201)
def add_finding(audit_id:int,body:FindingIn,current=Depends(user)):
    with connect() as db:
        if not db.execute("SELECT id FROM audits WHERE id=? AND tenant_id=?",(audit_id,current["tenant_id"])).fetchone(): raise HTTPException(404,"Audit not found")
        fid=db.execute("INSERT INTO findings(tenant_id,audit_id,title,severity,owner,due_on) VALUES(?,?,?,?,?,?)",(current["tenant_id"],audit_id,body.title.strip(),body.severity,body.owner.strip(),body.due_on.isoformat())).lastrowid
    return {"id":fid,"status":"open"}
@app.patch("/api/findings/{finding_id}")
def update_finding(finding_id:int,body:FindingUpdate,current=Depends(user)):
    with connect() as db:
        if not db.execute("SELECT id FROM findings WHERE id=? AND tenant_id=?",(finding_id,current["tenant_id"])).fetchone(): raise HTTPException(404,"Finding not found")
        db.execute("UPDATE findings SET status=?,remediation=?,verified_at=CASE WHEN ?='verified' THEN CURRENT_TIMESTAMP ELSE NULL END WHERE id=? AND tenant_id=?",(body.status,body.remediation.strip(),body.status,finding_id,current["tenant_id"]))
    return {"status":body.status}


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
from .security import hash_password,verify_password,token,decode
ROOT=Path(__file__).parent;bearer=HTTPBearer(auto_error=False)
@asynccontextmanager
async def lifespan(_): init_db();yield
app=FastAPI(title=os.getenv("APP_NAME","PrivacyMap"),lifespan=lifespan)
class Register(BaseModel): name:str=Field(min_length=2,max_length=80);workspace:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr;password:str
class ActivityIn(BaseModel):
    name:str=Field(min_length=2,max_length=140);owner:str=Field(min_length=2,max_length=100);purpose:str=Field(min_length=5,max_length=1000);lawful_basis:str;data_subjects:str=Field(min_length=2,max_length=200);retention_days:int=Field(ge=1,le=36500);review_due:date;risk:str
    @field_validator("lawful_basis")
    @classmethod
    def basis(cls,v):
        if v not in {"consent","contract","legal_obligation","legitimate_interest"}: raise ValueError("invalid lawful basis")
        return v
    @field_validator("risk")
    @classmethod
    def risk_value(cls,v):
        if v not in {"low","medium","high"}: raise ValueError("invalid risk")
        return v
class DataItemIn(BaseModel):
    category:str=Field(min_length=2,max_length=100);sensitive:bool=False;source:str=Field(min_length=2,max_length=120);recipient:str=Field(default="",max_length=120)
def user(c:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not c: raise HTTPException(401,"Authentication required")
    try:
        p=decode(c.credentials);return {"id":int(p["sub"]),"tenant_id":int(p["tenant_id"])}
    except (jwt.PyJWTError,KeyError,ValueError): raise HTTPException(401,"Invalid or expired token")
@app.get("/",response_class=HTMLResponse)
def home(): return (ROOT/"static"/"index.html").read_text()
@app.post("/api/auth/register",status_code=201)
def register(body:Register):
    try:
        with connect() as db:
            tid=db.execute("INSERT INTO tenants(name) VALUES(?)",(body.workspace.strip(),)).lastrowid;uid=db.execute("INSERT INTO users(tenant_id,name,email,password_hash) VALUES(?,?,?,?)",(tid,body.name.strip(),body.email.lower(),hash_password(body.password))).lastrowid
        return {"token":token(uid,tid)}
    except sqlite3.IntegrityError: raise HTTPException(409,"Email already registered")
@app.post("/api/auth/login")
def login(body:Login):
    with connect() as db: row=db.execute("SELECT * FROM users WHERE email=?",(body.email.lower(),)).fetchone()
    if not row or not verify_password(body.password,row["password_hash"]): raise HTTPException(401,"Invalid credentials")
    return {"token":token(row["id"],row["tenant_id"])}
@app.get("/api/dashboard")
def dashboard(current=Depends(user)):
    with connect() as db: rows=[dict(x) for x in db.execute("""SELECT a.*,COUNT(d.id) data_item_count,SUM(CASE WHEN d.sensitive=1 THEN 1 ELSE 0 END) sensitive_count FROM activities a LEFT JOIN data_items d ON d.activity_id=a.id AND d.tenant_id=a.tenant_id WHERE a.tenant_id=? GROUP BY a.id ORDER BY a.review_due""",(current["tenant_id"],))]
    return {"activities":rows,"summary":{"total":len(rows),"high_risk":sum(x["risk"]=="high" for x in rows),"reviews_due":sum(x["review_due"]<=date.today().isoformat() for x in rows)}}
@app.post("/api/activities",status_code=201)
def add_activity(body:ActivityIn,current=Depends(user)):
    try:
        with connect() as db:
            aid=db.execute("""INSERT INTO activities(tenant_id,name,owner,purpose,lawful_basis,data_subjects,retention_days,review_due,risk) VALUES(?,?,?,?,?,?,?,?,?)""",(current["tenant_id"],body.name.strip(),body.owner.strip(),body.purpose.strip(),body.lawful_basis,body.data_subjects.strip(),body.retention_days,body.review_due.isoformat(),body.risk)).lastrowid
        return {"id":aid,"status":"active"}
    except sqlite3.IntegrityError: raise HTTPException(409,"Activity already exists")
@app.post("/api/activities/{activity_id}/data-items",status_code=201)
def add_data(activity_id:int,body:DataItemIn,current=Depends(user)):
    with connect() as db:
        if not db.execute("SELECT id FROM activities WHERE id=? AND tenant_id=?",(activity_id,current["tenant_id"])).fetchone(): raise HTTPException(404,"Activity not found")
        did=db.execute("INSERT INTO data_items(tenant_id,activity_id,category,sensitive,source,recipient) VALUES(?,?,?,?,?,?)",(current["tenant_id"],activity_id,body.category.strip(),int(body.sensitive),body.source.strip(),body.recipient.strip())).lastrowid
    return {"id":did}
@app.patch("/api/activities/{activity_id}/status")
def set_status(activity_id:int,status_value:str,current=Depends(user)):
    if status_value not in {"draft","active","archived"}: raise HTTPException(422,"Invalid status")
    with connect() as db:
        if not db.execute("SELECT id FROM activities WHERE id=? AND tenant_id=?",(activity_id,current["tenant_id"])).fetchone(): raise HTTPException(404,"Activity not found")
        db.execute("UPDATE activities SET status=? WHERE id=? AND tenant_id=?",(status_value,activity_id,current["tenant_id"]))
    return {"status":status_value}


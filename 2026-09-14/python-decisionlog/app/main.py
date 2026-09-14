import os
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import jwt
from dotenv import load_dotenv
from fastapi import Depends,FastAPI,Header,HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel,EmailStr,Field,field_validator
from .db import connect,init_db
from .security import hash_password,verify_password,issue_token,read_token

load_dotenv(); STATES={"open","in_progress","done","cancelled"}
@asynccontextmanager
async def lifespan(_:FastAPI): init_db(); yield
app=FastAPI(title="DecisionLog",lifespan=lifespan)
class Register(BaseModel): organization:str=Field(min_length=2,max_length=80); email:EmailStr; password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr; password:str
class MeetingIn(BaseModel): title:str=Field(min_length=2,max_length=120); held_on:date; facilitator:str=Field(min_length=2,max_length=80); notes:str=Field(default="",max_length=3000)
class DecisionIn(BaseModel):
    meeting_id:int=Field(gt=0); summary:str=Field(min_length=3,max_length=300); rationale:str=Field(default="",max_length=2000); owner:str=Field(min_length=2,max_length=80); due_date:date|None=None; status:str="open"
    @field_validator("status")
    @classmethod
    def valid_status(cls,value):
        if value not in STATES: raise ValueError("invalid status")
        return value

def auth(authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401,"Missing bearer token")
    try:
        p=read_token(authorization[7:]); return {"id":int(p["sub"]),"tenant_id":int(p["tenant_id"])}
    except (jwt.PyJWTError,KeyError,ValueError): raise HTTPException(401,"Invalid or expired token")
def meeting_exists(meeting_id,tenant_id):
    with connect() as db: row=db.execute("SELECT 1 FROM meetings WHERE id=? AND tenant_id=?",(meeting_id,tenant_id)).fetchone()
    if not row: raise HTTPException(404,"Meeting not found")

@app.get("/",include_in_schema=False)
def index(): return FileResponse(Path(__file__).parent/"static"/"index.html")
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/api/auth/register",status_code=201)
def register(x:Register):
    with connect() as db:
        if db.execute("SELECT 1 FROM users WHERE lower(email)=lower(?)",(str(x.email),)).fetchone(): raise HTTPException(409,"Email already registered")
        tenant=db.execute("INSERT INTO tenants(name) VALUES(?)",(x.organization.strip(),)).lastrowid
        user=db.execute("INSERT INTO users(tenant_id,email,password_hash) VALUES(?,?,?)",(tenant,str(x.email).lower(),hash_password(x.password))).lastrowid
    return {"access_token":issue_token(user,tenant),"token_type":"bearer"}
@app.post("/api/auth/login")
def login(x:Login):
    with connect() as db: user=db.execute("SELECT * FROM users WHERE lower(email)=lower(?)",(str(x.email),)).fetchone()
    if not user or not verify_password(x.password,user["password_hash"]): raise HTTPException(401,"Invalid email or password")
    return {"access_token":issue_token(user["id"],user["tenant_id"]),"token_type":"bearer"}
@app.get("/api/meetings")
def meetings(user=Depends(auth)):
    with connect() as db: rows=db.execute("SELECT * FROM meetings WHERE tenant_id=? ORDER BY held_on DESC",(user["tenant_id"],)).fetchall()
    return [dict(r) for r in rows]
@app.post("/api/meetings",status_code=201)
def add_meeting(x:MeetingIn,user=Depends(auth)):
    with connect() as db:
        i=db.execute("INSERT INTO meetings(tenant_id,title,held_on,facilitator,notes) VALUES(?,?,?,?,?)",(user["tenant_id"],x.title.strip(),x.held_on.isoformat(),x.facilitator.strip(),x.notes.strip())).lastrowid
        row=db.execute("SELECT * FROM meetings WHERE id=? AND tenant_id=?",(i,user["tenant_id"])).fetchone()
    return dict(row)
@app.get("/api/decisions")
def decisions(user=Depends(auth)):
    with connect() as db: rows=db.execute("SELECT d.*,m.title meeting_title FROM decisions d JOIN meetings m ON m.id=d.meeting_id WHERE d.tenant_id=? ORDER BY d.status,d.due_date",(user["tenant_id"],)).fetchall()
    return [dict(r) for r in rows]
@app.post("/api/decisions",status_code=201)
def add_decision(x:DecisionIn,user=Depends(auth)):
    meeting_exists(x.meeting_id,user["tenant_id"])
    with connect() as db:
        i=db.execute("INSERT INTO decisions(tenant_id,meeting_id,summary,rationale,owner,due_date,status) VALUES(?,?,?,?,?,?,?)",(user["tenant_id"],x.meeting_id,x.summary.strip(),x.rationale.strip(),x.owner.strip(),x.due_date.isoformat() if x.due_date else None,x.status)).lastrowid
        row=db.execute("SELECT * FROM decisions WHERE id=? AND tenant_id=?",(i,user["tenant_id"])).fetchone()
    return dict(row)
@app.patch("/api/decisions/{decision_id}/status")
def change_status(decision_id:int,status:str,user=Depends(auth)):
    if status not in STATES: raise HTTPException(422,"Invalid status")
    with connect() as db:
        result=db.execute("UPDATE decisions SET status=? WHERE id=? AND tenant_id=?",(status,decision_id,user["tenant_id"]))
        if not result.rowcount: raise HTTPException(404,"Decision not found")
        row=db.execute("SELECT * FROM decisions WHERE id=?",(decision_id,)).fetchone()
    return dict(row)
@app.get("/api/dashboard")
def dashboard(user=Depends(auth)):
    with connect() as db: row=db.execute("SELECT COUNT(*) total,SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) completed,SUM(CASE WHEN status NOT IN ('done','cancelled') AND due_date < ? THEN 1 ELSE 0 END) overdue FROM decisions WHERE tenant_id=?",(date.today().isoformat(),user["tenant_id"])).fetchone()
    data=dict(row); data["completed"]=data["completed"] or 0; data["overdue"]=data["overdue"] or 0; return data

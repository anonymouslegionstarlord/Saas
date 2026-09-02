import os, sqlite3
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, model_validator
from .db import connect, init_db
from .security import create_token, decode_token, hash_password, verify_password

ROOT = Path(__file__).parent
bearer = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(_):
    init_db()
    yield

app = FastAPI(title=os.getenv("APP_NAME", "ContractCue"), lifespan=lifespan)

class Register(BaseModel):
    name: str = Field(min_length=2,max_length=80)
    workspace: str = Field(min_length=2,max_length=80)
    email: EmailStr
    password: str = Field(min_length=8,max_length=128)

class Login(BaseModel):
    email: EmailStr
    password: str

class ContractIn(BaseModel):
    title: str = Field(min_length=2,max_length=140)
    counterparty: str = Field(min_length=2,max_length=120)
    owner_email: EmailStr
    starts_on: date
    ends_on: date
    value_cents: int = Field(default=0,ge=0,le=100_000_000_000)
    notes: str = Field(default="",max_length=2000)
    @model_validator(mode="after")
    def dates(self):
        if self.ends_on < self.starts_on: raise ValueError("end date must not precede start date")
        return self

class ObligationIn(BaseModel):
    title: str = Field(min_length=2,max_length=180)
    due_on: date
    assignee: str = Field(min_length=2,max_length=100)

def current_user(credentials: HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not credentials: raise HTTPException(401,"Authentication required")
    try:
        claims=decode_token(credentials.credentials)
        return {"id":int(claims["sub"]),"tenant_id":int(claims["tenant_id"])}
    except (jwt.PyJWTError,KeyError,ValueError):
        raise HTTPException(401,"Invalid or expired token")

def owned_contract(db, contract_id, tenant_id):
    row=db.execute("SELECT * FROM contracts WHERE id=? AND tenant_id=?",(contract_id,tenant_id)).fetchone()
    if not row: raise HTTPException(404,"Contract not found")
    return row

@app.get("/",response_class=HTMLResponse)
def home(): return (ROOT/"static"/"index.html").read_text()

@app.post("/api/auth/register",status_code=201)
def register(body:Register):
    try:
        with connect() as db:
            tenant=db.execute("INSERT INTO tenants(name) VALUES(?)",(body.workspace.strip(),)).lastrowid
            user=db.execute("INSERT INTO users(tenant_id,name,email,password_hash) VALUES(?,?,?,?)",(tenant,body.name.strip(),body.email.lower(),hash_password(body.password))).lastrowid
        return {"token":create_token(user,tenant)}
    except sqlite3.IntegrityError: raise HTTPException(409,"Email already registered")

@app.post("/api/auth/login")
def login(body:Login):
    with connect() as db: row=db.execute("SELECT * FROM users WHERE email=?",(body.email.lower(),)).fetchone()
    if not row or not verify_password(body.password,row["password_hash"]): raise HTTPException(401,"Invalid credentials")
    return {"token":create_token(row["id"],row["tenant_id"])}

@app.get("/api/dashboard")
def dashboard(user=Depends(current_user)):
    with connect() as db:
        contracts=[dict(x) for x in db.execute("""SELECT c.*, COUNT(o.id) obligation_count,
        SUM(CASE WHEN o.status='open' AND o.due_on<=date('now','+14 day') THEN 1 ELSE 0 END) due_soon
        FROM contracts c LEFT JOIN obligations o ON o.contract_id=c.id AND o.tenant_id=c.tenant_id
        WHERE c.tenant_id=? GROUP BY c.id ORDER BY c.ends_on""",(user["tenant_id"],))]
    return {"contracts":contracts,"summary":{"total":len(contracts),"active":sum(x["status"]=="active" for x in contracts),"due_soon":sum(x["due_soon"] or 0 for x in contracts)}}

@app.post("/api/contracts",status_code=201)
def create_contract(body:ContractIn,user=Depends(current_user)):
    try:
        with connect() as db:
            cid=db.execute("""INSERT INTO contracts(tenant_id,title,counterparty,owner_email,starts_on,ends_on,value_cents,notes)
            VALUES(?,?,?,?,?,?,?,?)""",(user["tenant_id"],body.title.strip(),body.counterparty.strip(),body.owner_email,body.starts_on.isoformat(),body.ends_on.isoformat(),body.value_cents,body.notes.strip())).lastrowid
            row=db.execute("SELECT * FROM contracts WHERE id=?",(cid,)).fetchone()
        return dict(row)
    except sqlite3.IntegrityError: raise HTTPException(409,"Contract title already exists in this workspace")

@app.post("/api/contracts/{contract_id}/obligations",status_code=201)
def add_obligation(contract_id:int,body:ObligationIn,user=Depends(current_user)):
    with connect() as db:
        owned_contract(db,contract_id,user["tenant_id"])
        oid=db.execute("INSERT INTO obligations(tenant_id,contract_id,title,due_on,assignee) VALUES(?,?,?,?,?)",(user["tenant_id"],contract_id,body.title.strip(),body.due_on.isoformat(),body.assignee.strip())).lastrowid
    return {"id":oid,"status":"open"}

@app.patch("/api/obligations/{obligation_id}")
def update_obligation(obligation_id:int,status_value:str,user=Depends(current_user)):
    if status_value not in {"open","done","waived"}: raise HTTPException(422,"Invalid status")
    with connect() as db:
        row=db.execute("SELECT id FROM obligations WHERE id=? AND tenant_id=?",(obligation_id,user["tenant_id"])).fetchone()
        if not row: raise HTTPException(404,"Obligation not found")
        db.execute("UPDATE obligations SET status=?,completed_at=CASE WHEN ?='done' THEN CURRENT_TIMESTAMP ELSE NULL END WHERE id=? AND tenant_id=?",(status_value,status_value,obligation_id,user["tenant_id"]))
    return {"status":status_value}


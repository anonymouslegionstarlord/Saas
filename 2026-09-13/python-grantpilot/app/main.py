import os
from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field, field_validator

from .db import connect, init_db
from .security import create_token, decode_token, hash_password, verify_password

load_dotenv()
STATUSES = {"prospect", "drafting", "submitted", "awarded", "declined"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=os.getenv("APP_NAME", "GrantPilot"), lifespan=lifespan)


class Register(BaseModel):
    organization: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    email: EmailStr
    password: str


class GrantInput(BaseModel):
    funder: str = Field(min_length=2, max_length=100)
    program: str = Field(min_length=2, max_length=120)
    deadline: date
    requested_cents: int = Field(gt=0, le=1_000_000_000_00)
    awarded_cents: int = Field(default=0, ge=0, le=1_000_000_000_00)
    owner: str = Field(min_length=2, max_length=80)
    status: str = "prospect"
    notes: str = Field(default="", max_length=2000)

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        if value not in STATUSES:
            raise ValueError("invalid grant status")
        return value


def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    try:
        payload = decode_token(authorization[7:])
        return {"id": int(payload["sub"]), "tenant_id": int(payload["tenant_id"])}
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")


def grant_or_404(grant_id: int, tenant_id: int):
    with connect() as db:
        row = db.execute("SELECT * FROM grants WHERE id=? AND tenant_id=?", (grant_id, tenant_id)).fetchone()
    if not row:
        raise HTTPException(404, "Grant not found")
    return dict(row)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", status_code=201)
def register(payload: Register):
    with connect() as db:
        if db.execute("SELECT 1 FROM users WHERE lower(email)=lower(?)", (str(payload.email),)).fetchone():
            raise HTTPException(409, "Email already registered")
        cursor = db.execute("INSERT INTO tenants(name) VALUES(?)", (payload.organization.strip(),))
        tenant_id = cursor.lastrowid
        cursor = db.execute("INSERT INTO users(tenant_id,email,password_hash) VALUES(?,?,?)", (tenant_id, str(payload.email).lower(), hash_password(payload.password)))
        user_id = cursor.lastrowid
    return {"access_token": create_token(user_id, tenant_id, int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))), "token_type": "bearer"}


@app.post("/api/auth/login")
def login(payload: Login):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (str(payload.email),)).fetchone()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_token(user["id"], user["tenant_id"], int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))), "token_type": "bearer"}


@app.get("/api/grants")
def list_grants(user=Depends(current_user)):
    with connect() as db:
        rows = db.execute("SELECT * FROM grants WHERE tenant_id=? ORDER BY deadline", (user["tenant_id"],)).fetchall()
    return [dict(row) for row in rows]


@app.post("/api/grants", status_code=201)
def create_grant(payload: GrantInput, user=Depends(current_user)):
    with connect() as db:
        cursor = db.execute("""INSERT INTO grants(tenant_id,funder,program,deadline,requested_cents,awarded_cents,owner,status,notes)
          VALUES(?,?,?,?,?,?,?,?,?)""", (user["tenant_id"], payload.funder.strip(), payload.program.strip(), payload.deadline.isoformat(), payload.requested_cents, payload.awarded_cents, payload.owner.strip(), payload.status, payload.notes.strip()))
        grant_id = cursor.lastrowid
    return grant_or_404(grant_id, user["tenant_id"])


@app.put("/api/grants/{grant_id}")
def update_grant(grant_id: int, payload: GrantInput, user=Depends(current_user)):
    grant_or_404(grant_id, user["tenant_id"])
    with connect() as db:
        db.execute("""UPDATE grants SET funder=?,program=?,deadline=?,requested_cents=?,awarded_cents=?,owner=?,status=?,notes=? WHERE id=? AND tenant_id=?""",
          (payload.funder.strip(), payload.program.strip(), payload.deadline.isoformat(), payload.requested_cents, payload.awarded_cents, payload.owner.strip(), payload.status, payload.notes.strip(), grant_id, user["tenant_id"]))
    return grant_or_404(grant_id, user["tenant_id"])


@app.delete("/api/grants/{grant_id}", status_code=204)
def delete_grant(grant_id: int, user=Depends(current_user)):
    grant_or_404(grant_id, user["tenant_id"])
    with connect() as db:
        db.execute("DELETE FROM grants WHERE id=? AND tenant_id=?", (grant_id, user["tenant_id"]))


@app.get("/api/dashboard")
def dashboard(user=Depends(current_user)):
    today = date.today()
    soon = (today + timedelta(days=30)).isoformat()
    with connect() as db:
        row = db.execute("""SELECT COUNT(*) total, COALESCE(SUM(requested_cents),0) requested_cents,
          COALESCE(SUM(CASE WHEN status='awarded' THEN awarded_cents ELSE 0 END),0) awarded_cents,
          SUM(CASE WHEN deadline BETWEEN ? AND ? AND status NOT IN ('awarded','declined') THEN 1 ELSE 0 END) due_soon
          FROM grants WHERE tenant_id=?""", (today.isoformat(), soon, user["tenant_id"])).fetchone()
    return dict(row)


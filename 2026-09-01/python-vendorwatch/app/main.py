import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, field_validator

from .db import connect, init_db
from .security import create_token, decode_token, hash_password, verify_password

ROOT = Path(__file__).parent
bearer = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=os.getenv("APP_NAME", "VendorWatch"), lifespan=lifespan)


class Register(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    workspace: str = Field(min_length=2, max_length=80)


class Login(BaseModel):
    email: EmailStr
    password: str


class VendorIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    service: str = Field(min_length=2, max_length=120)
    owner_email: EmailStr
    data_access: str
    criticality: str
    next_review: date
    notes: str = Field(default="", max_length=1000)

    @field_validator("data_access")
    @classmethod
    def valid_access(cls, value):
        if value not in {"none", "internal", "confidential"}: raise ValueError("invalid data access")
        return value

    @field_validator("criticality")
    @classmethod
    def valid_criticality(cls, value):
        if value not in {"low", "medium", "high"}: raise ValueError("invalid criticality")
        return value


class AssessmentIn(BaseModel):
    security: int = Field(ge=1, le=5)
    privacy: int = Field(ge=1, le=5)
    resilience: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1000)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not credentials: raise HTTPException(status_code=401, detail="Authentication required")
    try:
        claims = decode_token(credentials.credentials)
        return {"id": int(claims["sub"]), "tenant_id": int(claims["tenant_id"])}
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def vendor_for_tenant(db, vendor_id: int, tenant_id: int):
    row = db.execute("SELECT * FROM vendors WHERE id=? AND tenant_id=?", (vendor_id, tenant_id)).fetchone()
    if not row: raise HTTPException(status_code=404, detail="Vendor not found")
    return row


@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "static" / "index.html").read_text()


@app.post("/api/auth/register", status_code=201)
def register(body: Register):
    try:
        with connect() as db:
            tenant = db.execute("INSERT INTO tenants(name) VALUES(?)", (body.workspace.strip(),)).lastrowid
            user = db.execute("INSERT INTO users(tenant_id,name,email,password_hash) VALUES(?,?,?,?)", (tenant, body.name.strip(), body.email.lower(), hash_password(body.password))).lastrowid
        return {"token": create_token(user, tenant)}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already registered")


@app.post("/api/auth/login")
def login(body: Login):
    with connect() as db: row = db.execute("SELECT * FROM users WHERE email=?", (body.email.lower(),)).fetchone()
    if not row or not verify_password(body.password, row["password_hash"]): raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(row["id"], row["tenant_id"])}


@app.get("/api/dashboard")
def dashboard(user=Depends(current_user)):
    with connect() as db:
        vendors = [dict(row) for row in db.execute("""SELECT v.*, ROUND(AVG((a.security+a.privacy+a.resilience)/3.0),1) risk_score
          FROM vendors v LEFT JOIN assessments a ON a.vendor_id=v.id AND a.tenant_id=v.tenant_id
          WHERE v.tenant_id=? GROUP BY v.id ORDER BY v.next_review""", (user["tenant_id"],))]
    return {"vendors": vendors, "summary": {"total": len(vendors), "high": sum(v["criticality"] == "high" for v in vendors), "due": sum(v["next_review"] <= date.today().isoformat() for v in vendors)}}


@app.post("/api/vendors", status_code=201)
def create_vendor(body: VendorIn, user=Depends(current_user)):
    try:
        with connect() as db:
            vendor_id = db.execute("""INSERT INTO vendors(tenant_id,name,service,owner_email,data_access,criticality,next_review,notes)
              VALUES(?,?,?,?,?,?,?,?)""", (user["tenant_id"], body.name.strip(), body.service.strip(), body.owner_email, body.data_access, body.criticality, body.next_review.isoformat(), body.notes.strip())).lastrowid
            row = db.execute("SELECT * FROM vendors WHERE id=?", (vendor_id,)).fetchone()
        return dict(row)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Vendor name already exists in this workspace")


@app.post("/api/vendors/{vendor_id}/assessments", status_code=201)
def assess(vendor_id: int, body: AssessmentIn, user=Depends(current_user)):
    with connect() as db:
        vendor_for_tenant(db, vendor_id, user["tenant_id"])
        assessment_id = db.execute("INSERT INTO assessments(tenant_id,vendor_id,security,privacy,resilience,comment) VALUES(?,?,?,?,?,?)", (user["tenant_id"], vendor_id, body.security, body.privacy, body.resilience, body.comment.strip())).lastrowid
    return {"id": assessment_id, "score": round((body.security + body.privacy + body.resilience) / 3, 1)}


@app.patch("/api/vendors/{vendor_id}/status")
def set_status(vendor_id: int, status_value: str, user=Depends(current_user)):
    if status_value not in {"review", "approved", "restricted"}: raise HTTPException(status_code=422, detail="Invalid status")
    with connect() as db:
        vendor_for_tenant(db, vendor_id, user["tenant_id"])
        db.execute("UPDATE vendors SET status=? WHERE id=? AND tenant_id=?", (status_value, vendor_id, user["tenant_id"]))
    return {"status": status_value}


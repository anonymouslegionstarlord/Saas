import os
import re
import secrets
import sqlite3
from pathlib import Path
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from .security import make_token, password_hash, password_matches, read_token
from .store import Store

SECRET = os.getenv("APP_SECRET", "development-only-change-me")
TTL = int(os.getenv("TOKEN_TTL_MINUTES", "120"))
store = Store(os.getenv("DATABASE_PATH", "./feedbackforge.db"))
app = FastAPI(title="FeedbackForge", version="1.0.0")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
oauth = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class Register(BaseModel):
    workspace: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class Login(BaseModel):
    email: EmailStr
    password: str

class Submission(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    details: str = Field(min_length=5, max_length=2000)
    customer_email: EmailStr

class Triage(BaseModel):
    status: str = Field(pattern="^(new|planned|shipped)$")
    priority: str = Field(pattern="^(low|medium|high)$")

def current_user(token: str = Depends(oauth)):
    try:
        payload = read_token(token, SECRET)
        user = store.user_id(int(payload["sub"]))
        if not user or user["tenant_id"] != payload["tid"]:
            raise ValueError
        return user
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid or expired token")

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/auth/register", status_code=201)
def register(data: Register):
    slug = re.sub(r"[^a-z0-9]+", "-", data.workspace.lower()).strip("-")
    try:
        user = store.register(data.workspace.strip(), slug, data.name.strip(), data.email, password_hash(data.password), secrets.token_urlsafe(12))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Workspace name or email already exists")
    return {"access_token": make_token(user["id"], user["tenant_id"], SECRET, TTL), "user": user}

@app.post("/api/auth/login")
def login(data: Login):
    user = store.user_email(data.email)
    if not user or not password_matches(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": make_token(user["id"], user["tenant_id"], SECRET, TTL)}

@app.get("/api/boards")
def boards(user=Depends(current_user)):
    return store.boards(user["tenant_id"])

@app.post("/api/public/boards/{public_key}/feedback", status_code=201)
def submit(public_key: str, data: Submission):
    result = store.submit(public_key, data.title.strip(), data.details.strip(), data.customer_email)
    if not result:
        raise HTTPException(404, "Board not found")
    return result

@app.get("/api/feedback")
def feedback(status: str | None = None, user=Depends(current_user)):
    if status and status not in {"new", "planned", "shipped"}:
        raise HTTPException(422, "Invalid status")
    return store.list_feedback(user["tenant_id"], status)

@app.patch("/api/feedback/{ident}")
def triage(ident: int, data: Triage, user=Depends(current_user)):
    result = store.update_feedback(user["tenant_id"], ident, data.status, data.priority)
    if not result:
        raise HTTPException(404, "Feedback not found")
    return result

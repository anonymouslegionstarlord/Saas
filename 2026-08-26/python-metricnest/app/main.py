import sqlite3
from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from .config import get_settings
from .security import decode_token, hash_password, issue_token, verify_password
from .store import Store

settings = get_settings()
store = Store(settings.database_path)
app = FastAPI(title="MetricNest", version="1.0.0")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Register(BaseModel):
    workspace: str = Field(min_length=2, max_length=60)
    name: str = Field(min_length=2, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    email: EmailStr
    password: str


class MetricIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    unit: str = Field(min_length=1, max_length=20)
    target: float = Field(ge=0)
    owner: str = Field(min_length=2, max_length=60)


class CheckinIn(BaseModel):
    value: float
    note: str = Field(default="", max_length=240)
    recorded_on: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")


def current_user(token: str = Depends(oauth2)):
    try:
        payload = decode_token(token, settings.secret)
        user = store.user_by_id(int(payload["sub"]))
        if not user or user["workspace_id"] != payload["wid"]:
            raise ValueError
        return user
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: Register):
    try:
        user = store.create_workspace_user(payload.workspace.strip(), payload.name.strip(), payload.email, hash_password(payload.password))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Email is already registered")
    return {"access_token": issue_token(user["id"], user["workspace_id"], settings.secret, settings.token_minutes), "token_type": "bearer", "user": user}


@app.post("/api/auth/login")
def login(payload: Login):
    user = store.user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    public = {key: user[key] for key in ("id", "workspace_id", "name", "email", "workspace")}
    return {"access_token": issue_token(user["id"], user["workspace_id"], settings.secret, settings.token_minutes), "token_type": "bearer", "user": public}


@app.get("/api/me")
def me(user=Depends(current_user)):
    return user


@app.get("/api/metrics")
def list_metrics(user=Depends(current_user)):
    return store.list_metrics(user["workspace_id"])


@app.post("/api/metrics", status_code=201)
def create_metric(payload: MetricIn, user=Depends(current_user)):
    return store.create_metric(user["workspace_id"], payload.name.strip(), payload.unit.strip(), payload.target, payload.owner.strip())


@app.post("/api/metrics/{metric_id}/checkins", status_code=201)
def add_checkin(metric_id: int, payload: CheckinIn, user=Depends(current_user)):
    result = store.add_checkin(user["workspace_id"], metric_id, payload.value, payload.note.strip(), payload.recorded_on)
    if not result:
        raise HTTPException(404, "Metric not found")
    return result


@app.delete("/api/metrics/{metric_id}", status_code=204)
def delete_metric(metric_id: int, user=Depends(current_user)):
    if not store.delete_metric(user["workspace_id"], metric_id):
        raise HTTPException(404, "Metric not found")

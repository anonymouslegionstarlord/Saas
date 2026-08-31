import os,secrets,sqlite3
from pathlib import Path
import jwt
from fastapi import Depends,FastAPI,HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,EmailStr,Field
from .security import decode_token,hash_password,issue_token,verify_password
from .store import Store
SECRET=os.getenv("APP_SECRET","development-only-change-me");TTL=int(os.getenv("TOKEN_TTL_MINUTES","120"));store=Store(os.getenv("DATABASE_PATH","./incidentatlas.db"))
app=FastAPI(title="IncidentAtlas",version="1.0.0");app.mount("/static",StaticFiles(directory=Path(__file__).parent/"static"),name="static");oauth=OAuth2PasswordBearer(tokenUrl="/api/auth/login")
class Register(BaseModel):
    workspace:str=Field(min_length=2,max_length=80);name:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel):email:EmailStr;password:str
class IncidentIn(BaseModel):
    title:str=Field(min_length=3,max_length=120);severity:str=Field(pattern="^(minor|major|critical)$");summary:str=Field(min_length=10,max_length=1000)
class UpdateIn(BaseModel):
    status:str=Field(pattern="^(investigating|identified|monitoring|resolved)$");message:str=Field(min_length=5,max_length=1500)
def current_user(token:str=Depends(oauth)):
    try:
        payload=decode_token(token,SECRET);user=store.user_id(int(payload["sub"]))
        if not user or user["workspace_id"]!=payload["wid"]:raise ValueError
        return user
    except (jwt.PyJWTError,KeyError,ValueError):raise HTTPException(401,"Invalid or expired token")
@app.get("/",include_in_schema=False)
def home():return FileResponse(Path(__file__).parent/"static"/"index.html")
@app.get("/health")
def health():return {"status":"ok"}
@app.post("/api/auth/register",status_code=201)
def register(data:Register):
    try:user=store.register(data.workspace.strip(),secrets.token_urlsafe(12),data.name.strip(),data.email,hash_password(data.password))
    except sqlite3.IntegrityError:raise HTTPException(409,"Email already registered")
    return {"access_token":issue_token(user["id"],user["workspace_id"],SECRET,TTL),"user":user}
@app.post("/api/auth/login")
def login(data:Login):
    user=store.user_email(data.email)
    if not user or not verify_password(data.password,user["password_hash"]):raise HTTPException(401,"Invalid email or password")
    return {"access_token":issue_token(user["id"],user["workspace_id"],SECRET,TTL)}
@app.get("/api/me")
def me(user=Depends(current_user)):return user
@app.get("/api/incidents")
def incidents(user=Depends(current_user)):return store.list_incidents(user["workspace_id"])
@app.post("/api/incidents",status_code=201)
def create(data:IncidentIn,user=Depends(current_user)):return store.create_incident(user["workspace_id"],data.model_dump())
@app.post("/api/incidents/{ident}/updates",status_code=201)
def update(ident:int,data:UpdateIn,user=Depends(current_user)):
    result=store.add_update(user["workspace_id"],ident,data.status,data.message.strip())
    if not result:raise HTTPException(404,"Incident not found")
    return result
@app.get("/api/public/status/{key}")
def public_status(key:str):
    result=store.public_status(key)
    if not result:raise HTTPException(404,"Status page not found")
    return result

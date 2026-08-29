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
SECRET=os.getenv("APP_SECRET","development-only-change-me");TTL=int(os.getenv("TOKEN_TTL_MINUTES","120"));store=Store(os.getenv("DATABASE_PATH","./policypulse.db"))
app=FastAPI(title="PolicyPulse",version="1.0.0");app.mount("/static",StaticFiles(directory=Path(__file__).parent/"static"),name="static");oauth=OAuth2PasswordBearer(tokenUrl="/api/auth/login")
class Register(BaseModel):
    workspace:str=Field(min_length=2,max_length=80);name:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel):email:EmailStr;password:str
class PolicyIn(BaseModel):
    title:str=Field(min_length=3,max_length=120);version:str=Field(min_length=1,max_length=20);content:str=Field(min_length=20,max_length=10000)
class AckIn(BaseModel):
    employee_name:str=Field(min_length=2,max_length=80);employee_email:EmailStr;accepted:bool
class ActiveIn(BaseModel):active:bool
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
    try:user=store.register(data.workspace.strip(),data.name.strip(),data.email,hash_password(data.password))
    except sqlite3.IntegrityError:raise HTTPException(409,"Email already registered")
    return {"access_token":issue_token(user["id"],user["workspace_id"],SECRET,TTL),"user":user}
@app.post("/api/auth/login")
def login(data:Login):
    user=store.user_email(data.email)
    if not user or not verify_password(data.password,user["password_hash"]):raise HTTPException(401,"Invalid email or password")
    return {"access_token":issue_token(user["id"],user["workspace_id"],SECRET,TTL)}
@app.get("/api/policies")
def policies(user=Depends(current_user)):return store.list_policies(user["workspace_id"])
@app.post("/api/policies",status_code=201)
def create(data:PolicyIn,user=Depends(current_user)):
    try:return store.create_policy(user["workspace_id"],data.title.strip(),data.version.strip(),data.content.strip(),secrets.token_urlsafe(12))
    except sqlite3.IntegrityError:raise HTTPException(409,"This policy version already exists")
@app.patch("/api/policies/{ident}")
def toggle(ident:int,data:ActiveIn,user=Depends(current_user)):
    result=store.toggle(user["workspace_id"],ident,data.active)
    if not result:raise HTTPException(404,"Policy not found")
    return result
@app.get("/api/policies/{ident}/acknowledgements")
def acknowledgements(ident:int,user=Depends(current_user)):
    result=store.acknowledgements(user["workspace_id"],ident)
    if result is None:raise HTTPException(404,"Policy not found")
    return result
@app.get("/api/public/policies/{key}")
def public_policy(key:str):
    result=store.public_policy(key)
    if not result:raise HTTPException(404,"Active policy not found")
    return result
@app.post("/api/public/policies/{key}/acknowledge",status_code=201)
def acknowledge(key:str,data:AckIn):
    if not data.accepted:raise HTTPException(422,"Policy acceptance is required")
    try:result=store.acknowledge(key,data.employee_name.strip(),data.employee_email)
    except sqlite3.IntegrityError:raise HTTPException(409,"This employee already acknowledged the policy")
    if not result:raise HTTPException(404,"Active policy not found")
    return result

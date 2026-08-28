import os
import sqlite3
from datetime import date
from pathlib import Path
import jwt
from fastapi import Depends,FastAPI,HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,EmailStr,Field,field_validator
from .security import decode_token,hash_password,issue_token,verify_password
from .store import Store

SECRET=os.getenv("APP_SECRET","development-only-change-me")
TTL=int(os.getenv("TOKEN_TTL_MINUTES","120"))
store=Store(os.getenv("DATABASE_PATH","./renewalradar.db"))
app=FastAPI(title="RenewalRadar",version="1.0.0")
app.mount("/static",StaticFiles(directory=Path(__file__).parent/"static"),name="static")
oauth=OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class Register(BaseModel):
    workspace:str=Field(min_length=2,max_length=80)
    name:str=Field(min_length=2,max_length=80)
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)

class Login(BaseModel):
    email:EmailStr
    password:str

class SubscriptionIn(BaseModel):
    vendor:str=Field(min_length=2,max_length=100)
    category:str=Field(min_length=2,max_length=60)
    cost:float=Field(ge=0)
    billing_cycle:str=Field(pattern="^(monthly|quarterly|yearly)$")
    renewal_date:str=Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    owner:str=Field(min_length=2,max_length=80)
    notes:str=Field(default="",max_length=500)

    @field_validator("renewal_date")
    @classmethod
    def valid_date(cls,value):
        date.fromisoformat(value)
        return value

class ActiveIn(BaseModel):
    active:bool

def current_user(token:str=Depends(oauth)):
    try:
        payload=decode_token(token,SECRET)
        user=store.user_by_id(int(payload["sub"]))
        if not user or user["workspace_id"]!=payload["wid"]:
            raise ValueError
        return user
    except (jwt.PyJWTError,KeyError,ValueError):
        raise HTTPException(401,"Invalid or expired token")

@app.get("/",include_in_schema=False)
def home():
    return FileResponse(Path(__file__).parent/"static"/"index.html")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/api/auth/register",status_code=201)
def register(data:Register):
    try:
        user=store.register(data.workspace.strip(),data.name.strip(),data.email,hash_password(data.password))
    except sqlite3.IntegrityError:
        raise HTTPException(409,"Email already registered")
    return {"access_token":issue_token(user["id"],user["workspace_id"],SECRET,TTL),"user":user}

@app.post("/api/auth/login")
def login(data:Login):
    user=store.user_by_email(data.email)
    if not user or not verify_password(data.password,user["password_hash"]):
        raise HTTPException(401,"Invalid email or password")
    return {"access_token":issue_token(user["id"],user["workspace_id"],SECRET,TTL)}

@app.get("/api/subscriptions")
def subscriptions(user=Depends(current_user)):
    return store.list_subscriptions(user["workspace_id"])

@app.post("/api/subscriptions",status_code=201)
def create(data:SubscriptionIn,user=Depends(current_user)):
    return store.create_subscription(user["workspace_id"],data.model_dump())

@app.patch("/api/subscriptions/{ident}")
def toggle(ident:int,data:ActiveIn,user=Depends(current_user)):
    result=store.update_subscription(user["workspace_id"],ident,data.active)
    if not result:
        raise HTTPException(404,"Subscription not found")
    return result

@app.delete("/api/subscriptions/{ident}",status_code=204)
def delete(ident:int,user=Depends(current_user)):
    if not store.delete_subscription(user["workspace_id"],ident):
        raise HTTPException(404,"Subscription not found")

@app.get("/api/summary")
def summary(user=Depends(current_user)):
    return store.summary(user["workspace_id"])

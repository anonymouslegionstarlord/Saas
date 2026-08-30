import os,sqlite3
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
SECRET=os.getenv("APP_SECRET","development-only-change-me");TTL=int(os.getenv("TOKEN_TTL_MINUTES","120"));store=Store(os.getenv("DATABASE_PATH","./leaveledger.db"))
app=FastAPI(title="LeaveLedger",version="1.0.0");app.mount("/static",StaticFiles(directory=Path(__file__).parent/"static"),name="static");oauth=OAuth2PasswordBearer(tokenUrl="/api/auth/login")
class Register(BaseModel):
    workspace:str=Field(min_length=2,max_length=80);name:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel):email:EmailStr;password:str
class RequestIn(BaseModel):
    employee_name:str=Field(min_length=2,max_length=80);employee_email:EmailStr;leave_type:str=Field(pattern="^(annual|sick|unpaid)$");start_date:str=Field(pattern=r"^\d{4}-\d{2}-\d{2}$");end_date:str=Field(pattern=r"^\d{4}-\d{2}-\d{2}$");reason:str=Field(min_length=5,max_length=500)
    @field_validator("start_date","end_date")
    @classmethod
    def valid_date(cls,value):date.fromisoformat(value);return value
class DecisionIn(BaseModel):status:str=Field(pattern="^(approved|rejected)$")
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
@app.get("/api/requests")
def requests(status:str|None=None,user=Depends(current_user)):
    if status and status not in {"pending","approved","rejected"}:raise HTTPException(422,"Invalid status")
    return store.list_requests(user["workspace_id"],status)
@app.post("/api/requests",status_code=201)
def create(data:RequestIn,user=Depends(current_user)):
    try:return store.create_request(user["workspace_id"],data.model_dump())
    except ValueError as error:raise HTTPException(422,str(error))
@app.patch("/api/requests/{ident}")
def decide(ident:int,data:DecisionIn,user=Depends(current_user)):
    result=store.decide(user["workspace_id"],ident,data.status)
    if not result:raise HTTPException(404,"Pending request not found")
    return result
@app.get("/api/summary")
def summary(user=Depends(current_user)):return store.summary(user["workspace_id"])

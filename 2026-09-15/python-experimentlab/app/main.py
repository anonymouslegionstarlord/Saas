import os
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import jwt
from dotenv import load_dotenv
from fastapi import Depends,FastAPI,Header,HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel,EmailStr,Field,field_validator,model_validator
from .db import connect,init_db
from .security import create_token,decode_token,hash_password,verify_password
load_dotenv();STATES={'draft','running','won','lost','inconclusive'}
@asynccontextmanager
async def lifespan(_:FastAPI):init_db();yield
app=FastAPI(title='ExperimentLab',lifespan=lifespan)
class Register(BaseModel):organization:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel):email:EmailStr;password:str
class ExperimentIn(BaseModel):
    name:str=Field(min_length=2,max_length=120);hypothesis:str=Field(min_length=5,max_length=1000);primary_metric:str=Field(min_length=2,max_length=100);target_lift:float=Field(gt=0,le=1000);starts_on:date;ends_on:date;status:str='draft';baseline:float|None=Field(default=None,ge=0);observed:float|None=Field(default=None,ge=0);notes:str=Field(default='',max_length=2000)
    @field_validator('status')
    @classmethod
    def status_ok(cls,v):
        if v not in STATES:raise ValueError('invalid status')
        return v
    @model_validator(mode='after')
    def dates_ok(self):
        if self.ends_on<=self.starts_on:raise ValueError('ends_on must be after starts_on')
        return self
class ResultIn(BaseModel):status:str;baseline:float=Field(ge=0);observed:float=Field(ge=0);notes:str=Field(default='',max_length=2000)
    
def current_user(authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Missing bearer token')
    try:p=decode_token(authorization[7:]);return {'id':int(p['sub']),'tenant_id':int(p['tenant_id'])}
    except (jwt.PyJWTError,KeyError,ValueError):raise HTTPException(401,'Invalid or expired token')
def get_one(i,tid):
    with connect() as db:r=db.execute('SELECT * FROM experiments WHERE id=? AND tenant_id=?',(i,tid)).fetchone()
    if not r:raise HTTPException(404,'Experiment not found')
    return dict(r)
@app.get('/',include_in_schema=False)
def index():return FileResponse(Path(__file__).parent/'static'/'index.html')
@app.get('/health')
def health():return {'status':'ok'}
@app.post('/api/auth/register',status_code=201)
def register(x:Register):
    with connect() as db:
        if db.execute('SELECT 1 FROM users WHERE lower(email)=lower(?)',(str(x.email),)).fetchone():raise HTTPException(409,'Email already registered')
        tid=db.execute('INSERT INTO tenants(name) VALUES(?)',(x.organization.strip(),)).lastrowid;uid=db.execute('INSERT INTO users(tenant_id,email,password_hash) VALUES(?,?,?)',(tid,str(x.email).lower(),hash_password(x.password))).lastrowid
    return {'access_token':create_token(uid,tid),'token_type':'bearer'}
@app.post('/api/auth/login')
def login(x:Login):
    with connect() as db:u=db.execute('SELECT * FROM users WHERE lower(email)=lower(?)',(str(x.email),)).fetchone()
    if not u or not verify_password(x.password,u['password_hash']):raise HTTPException(401,'Invalid email or password')
    return {'access_token':create_token(u['id'],u['tenant_id']),'token_type':'bearer'}
@app.get('/api/experiments')
def list_all(user=Depends(current_user)):
    with connect() as db:rows=db.execute('SELECT * FROM experiments WHERE tenant_id=? ORDER BY starts_on DESC',(user['tenant_id'],)).fetchall()
    return [dict(r) for r in rows]
@app.post('/api/experiments',status_code=201)
def create(x:ExperimentIn,user=Depends(current_user)):
    with connect() as db:i=db.execute('INSERT INTO experiments(tenant_id,name,hypothesis,primary_metric,target_lift,starts_on,ends_on,status,baseline,observed,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(user['tenant_id'],x.name.strip(),x.hypothesis.strip(),x.primary_metric.strip(),x.target_lift,x.starts_on.isoformat(),x.ends_on.isoformat(),x.status,x.baseline,x.observed,x.notes.strip())).lastrowid
    return get_one(i,user['tenant_id'])
@app.patch('/api/experiments/{experiment_id}/result')
def result(experiment_id:int,x:ResultIn,user=Depends(current_user)):
    if x.status not in {'won','lost','inconclusive'}:raise HTTPException(422,'Result status must be won, lost, or inconclusive')
    get_one(experiment_id,user['tenant_id'])
    with connect() as db:db.execute('UPDATE experiments SET status=?,baseline=?,observed=?,notes=? WHERE id=? AND tenant_id=?',(x.status,x.baseline,x.observed,x.notes.strip(),experiment_id,user['tenant_id']))
    return get_one(experiment_id,user['tenant_id'])
@app.delete('/api/experiments/{experiment_id}',status_code=204)
def delete(experiment_id:int,user=Depends(current_user)):
    get_one(experiment_id,user['tenant_id'])
    with connect() as db:db.execute('DELETE FROM experiments WHERE id=? AND tenant_id=?',(experiment_id,user['tenant_id']))
@app.get('/api/dashboard')
def dashboard(user=Depends(current_user)):
    with connect() as db:r=db.execute("SELECT COUNT(*) total,SUM(CASE WHEN status='running' THEN 1 ELSE 0 END) running,SUM(CASE WHEN status='won' THEN 1 ELSE 0 END) wins,AVG(CASE WHEN baseline>0 AND observed IS NOT NULL THEN ((observed-baseline)/baseline)*100 END) average_lift FROM experiments WHERE tenant_id=?",(user['tenant_id'],)).fetchone()
    d=dict(r);d['running']=d['running'] or 0;d['wins']=d['wins'] or 0;d['average_lift']=round(d['average_lift'] or 0,2);return d


import os,sqlite3
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import jwt
from fastapi import Depends,FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from pydantic import BaseModel,EmailStr,Field,field_validator
from .db import connect,init_db
from .security import create_token,decode_token,hash_password,verify_password
ROOT=Path(__file__).parent;bearer=HTTPBearer(auto_error=False)
@asynccontextmanager
async def lifespan(_): init_db();yield
app=FastAPI(title=os.getenv('APP_NAME','TimeLedger'),lifespan=lifespan)
class Register(BaseModel): name:str=Field(min_length=2,max_length=80);workspace:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr;password:str
class ProjectIn(BaseModel): name:str=Field(min_length=2,max_length=120);client:str=Field(min_length=2,max_length=120);hourly_rate_cents:int=Field(ge=0,le=100000000);budget_hours:float=Field(gt=0,le=100000)
class EntryIn(BaseModel): worked_on:date;hours:float=Field(gt=0,le=24);task:str=Field(min_length=3,max_length=500);billable:bool=True
class ReviewIn(BaseModel):
    status:str;review_note:str=Field(min_length=3,max_length=500)
    @field_validator('status')
    @classmethod
    def status_value(cls,v):
        if v not in {'approved','rejected'}: raise ValueError('invalid review status')
        return v
def user(c:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not c: raise HTTPException(401,'Authentication required')
    try:
        p=decode_token(c.credentials);return {'id':int(p['sub']),'tenant_id':int(p['tenant_id'])}
    except (jwt.PyJWTError,KeyError,ValueError): raise HTTPException(401,'Invalid or expired token')
@app.get('/',response_class=HTMLResponse)
def home(): return (ROOT/'static'/'index.html').read_text()
@app.post('/api/auth/register',status_code=201)
def register(body:Register):
    try:
        with connect() as db:
            tid=db.execute('INSERT INTO tenants(name) VALUES(?)',(body.workspace.strip(),)).lastrowid;uid=db.execute('INSERT INTO users(tenant_id,name,email,password_hash) VALUES(?,?,?,?)',(tid,body.name.strip(),body.email.lower(),hash_password(body.password))).lastrowid
        return {'token':create_token(uid,tid)}
    except sqlite3.IntegrityError: raise HTTPException(409,'Email already registered')
@app.post('/api/auth/login')
def login(body:Login):
    with connect() as db: row=db.execute('SELECT * FROM users WHERE email=?',(body.email.lower(),)).fetchone()
    if not row or not verify_password(body.password,row['password_hash']): raise HTTPException(401,'Invalid credentials')
    return {'token':create_token(row['id'],row['tenant_id'])}
@app.get('/api/dashboard')
def dashboard(current=Depends(user)):
    with connect() as db:
        projects=[dict(x) for x in db.execute('SELECT * FROM projects WHERE tenant_id=? ORDER BY name',(current['tenant_id'],))];result=[]
        for p in projects:
            entries=[dict(x) for x in db.execute('SELECT * FROM entries WHERE tenant_id=? AND project_id=? ORDER BY worked_on DESC,created_at DESC',(current['tenant_id'],p['id']))];approved=sum(x['hours'] for x in entries if x['status']=='approved');result.append({**p,'entries':entries,'approved_hours':approved,'budget_used_percent':round(approved/p['budget_hours']*100,1)})
    all_entries=[x for p in result for x in p['entries']];approved_value=sum(round(x['hours']*p['hourly_rate_cents']) for p in result for x in p['entries'] if x['status']=='approved' and x['billable'])
    return {'projects':result,'summary':{'submitted_hours':round(sum(x['hours'] for x in all_entries if x['status']=='submitted'),2),'approved_hours':round(sum(x['hours'] for x in all_entries if x['status']=='approved'),2),'approved_billable_cents':approved_value}}
@app.post('/api/projects',status_code=201)
def add_project(body:ProjectIn,current=Depends(user)):
    try:
        with connect() as db: pid=db.execute('INSERT INTO projects(tenant_id,name,client,hourly_rate_cents,budget_hours) VALUES(?,?,?,?,?)',(current['tenant_id'],body.name.strip(),body.client.strip(),body.hourly_rate_cents,body.budget_hours)).lastrowid
        return {'id':pid}
    except sqlite3.IntegrityError: raise HTTPException(409,'Project already exists in this workspace')
@app.post('/api/projects/{project_id}/entries',status_code=201)
def add_entry(project_id:int,body:EntryIn,current=Depends(user)):
    with connect() as db:
        if not db.execute('SELECT id FROM projects WHERE id=? AND tenant_id=?',(project_id,current['tenant_id'])).fetchone(): raise HTTPException(404,'Project not found')
        eid=db.execute('INSERT INTO entries(tenant_id,project_id,worked_on,hours,task,billable) VALUES(?,?,?,?,?,?)',(current['tenant_id'],project_id,body.worked_on.isoformat(),body.hours,body.task.strip(),int(body.billable))).lastrowid
    return {'id':eid,'status':'submitted'}
@app.patch('/api/entries/{entry_id}/review')
def review(entry_id:int,body:ReviewIn,current=Depends(user)):
    with connect() as db:
        row=db.execute('SELECT status FROM entries WHERE id=? AND tenant_id=?',(entry_id,current['tenant_id'])).fetchone()
        if not row: raise HTTPException(404,'Time entry not found')
        if row['status']!='submitted': raise HTTPException(409,'Time entry has already been reviewed')
        db.execute('UPDATE entries SET status=?,review_note=?,reviewed_at=CURRENT_TIMESTAMP WHERE id=? AND tenant_id=?',(body.status,body.review_note.strip(),entry_id,current['tenant_id']))
    return {'status':body.status}


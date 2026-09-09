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
app=FastAPI(title=os.getenv('APP_NAME','MeterMind'),lifespan=lifespan)
class Register(BaseModel): name:str=Field(min_length=2,max_length=80);workspace:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr;password:str
class MeterIn(BaseModel):
    name:str=Field(min_length=2,max_length=120);location:str=Field(min_length=2,max_length=180);unit:str;alert_percent:int=Field(ge=1,le=500)
    @field_validator('unit')
    @classmethod
    def unit_value(cls,v):
        if v not in {'kWh','litres','m3'}: raise ValueError('invalid unit')
        return v
class ReadingIn(BaseModel): reading_on:date;value:float=Field(ge=0,le=1000000000000);note:str=Field(default='',max_length=500)
def user(c:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not c: raise HTTPException(401,'Authentication required')
    try:
        p=decode_token(c.credentials);return {'id':int(p['sub']),'tenant_id':int(p['tenant_id'])}
    except (jwt.PyJWTError,KeyError,ValueError): raise HTTPException(401,'Invalid or expired token')
def enrich(meter,readings):
    values=[]
    for i,r in enumerate(readings): values.append({**r,'usage':None if i==0 else round(r['value']-readings[i-1]['value'],3)})
    latest=values[-1]['usage'] if values else None;previous=values[-2]['usage'] if len(values)>2 else None
    return {**meter,'readings':list(reversed(values)),'latest_usage':latest,'anomaly':bool(latest is not None and previous is not None and previous>0 and latest>previous*(1+meter['alert_percent']/100))}
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
        meters=[dict(x) for x in db.execute('SELECT * FROM meters WHERE tenant_id=? ORDER BY name',(current['tenant_id'],))];result=[]
        for m in meters: result.append(enrich(m,[dict(x) for x in db.execute('SELECT * FROM readings WHERE tenant_id=? AND meter_id=? ORDER BY reading_on',(current['tenant_id'],m['id']))]))
    return {'meters':result,'summary':{'meters':len(result),'anomalies':sum(x['anomaly'] for x in result),'latest_usage':round(sum(x['latest_usage'] or 0 for x in result),3)}}
@app.post('/api/meters',status_code=201)
def add_meter(body:MeterIn,current=Depends(user)):
    try:
        with connect() as db: mid=db.execute('INSERT INTO meters(tenant_id,name,location,unit,alert_percent) VALUES(?,?,?,?,?)',(current['tenant_id'],body.name.strip(),body.location.strip(),body.unit,body.alert_percent)).lastrowid
        return {'id':mid}
    except sqlite3.IntegrityError: raise HTTPException(409,'Meter name already exists in this workspace')
@app.post('/api/meters/{meter_id}/readings',status_code=201)
def add_reading(meter_id:int,body:ReadingIn,current=Depends(user)):
    with connect() as db:
        if not db.execute('SELECT id FROM meters WHERE id=? AND tenant_id=?',(meter_id,current['tenant_id'])).fetchone(): raise HTTPException(404,'Meter not found')
        last=db.execute('SELECT value,reading_on FROM readings WHERE meter_id=? AND tenant_id=? ORDER BY reading_on DESC LIMIT 1',(meter_id,current['tenant_id'])).fetchone()
        if last and (body.reading_on.isoformat()<=last['reading_on'] or body.value<last['value']): raise HTTPException(422,'Reading must be later and not lower than the previous reading')
        try: rid=db.execute('INSERT INTO readings(tenant_id,meter_id,reading_on,value,note) VALUES(?,?,?,?,?)',(current['tenant_id'],meter_id,body.reading_on.isoformat(),body.value,body.note.strip())).lastrowid
        except sqlite3.IntegrityError: raise HTTPException(409,'Reading already exists for this date')
    return {'id':rid}

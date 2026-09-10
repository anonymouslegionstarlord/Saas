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
app=FastAPI(title=os.getenv('APP_NAME','FleetLedger'),lifespan=lifespan)
class Register(BaseModel): name:str=Field(min_length=2,max_length=80);workspace:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr;password:str
class VehicleIn(BaseModel):
    registration:str=Field(min_length=3,max_length=20,pattern=r'^[A-Za-z0-9 -]+$');label:str=Field(min_length=2,max_length=100);fuel_type:str;efficiency_floor:float=Field(gt=0,le=100)
    @field_validator('fuel_type')
    @classmethod
    def fuel_value(cls,v):
        if v not in {'petrol','diesel','cng'}: raise ValueError('invalid fuel type')
        return v
class FuelLogIn(BaseModel): filled_on:date;odometer_km:float=Field(ge=0,le=10000000);litres:float=Field(gt=0,le=10000);cost_cents:int=Field(gt=0,le=1000000000);driver:str=Field(min_length=2,max_length=100);note:str=Field(default='',max_length=500)
def user(c:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not c: raise HTTPException(401,'Authentication required')
    try:
        p=decode_token(c.credentials);return {'id':int(p['sub']),'tenant_id':int(p['tenant_id'])}
    except (jwt.PyJWTError,KeyError,ValueError): raise HTTPException(401,'Invalid or expired token')
def enrich(vehicle,logs):
    rows=[]
    for i,log in enumerate(logs):
        distance=None if i==0 else round(log['odometer_km']-logs[i-1]['odometer_km'],2);efficiency=None if distance is None else round(distance/log['litres'],2)
        rows.append({**log,'distance_km':distance,'efficiency':efficiency})
    latest=rows[-1]['efficiency'] if rows else None
    return {**vehicle,'logs':list(reversed(rows)),'latest_efficiency':latest,'low_efficiency':bool(latest is not None and latest<vehicle['efficiency_floor']),'total_cost_cents':sum(x['cost_cents'] for x in logs)}
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
        vehicles=[dict(x) for x in db.execute('SELECT * FROM vehicles WHERE tenant_id=? ORDER BY registration',(current['tenant_id'],))];result=[]
        for v in vehicles: result.append(enrich(v,[dict(x) for x in db.execute('SELECT * FROM fuel_logs WHERE tenant_id=? AND vehicle_id=? ORDER BY filled_on,odometer_km',(current['tenant_id'],v['id']))]))
    return {'vehicles':result,'summary':{'vehicles':len(result),'low_efficiency':sum(x['low_efficiency'] for x in result),'total_cost_cents':sum(x['total_cost_cents'] for x in result)}}
@app.post('/api/vehicles',status_code=201)
def add_vehicle(body:VehicleIn,current=Depends(user)):
    try:
        with connect() as db: vid=db.execute('INSERT INTO vehicles(tenant_id,registration,label,fuel_type,efficiency_floor) VALUES(?,?,?,?,?)',(current['tenant_id'],body.registration.upper().strip(),body.label.strip(),body.fuel_type,body.efficiency_floor)).lastrowid
        return {'id':vid}
    except sqlite3.IntegrityError: raise HTTPException(409,'Registration already exists in this workspace')
@app.post('/api/vehicles/{vehicle_id}/fuel-logs',status_code=201)
def add_log(vehicle_id:int,body:FuelLogIn,current=Depends(user)):
    with connect() as db:
        if not db.execute('SELECT id FROM vehicles WHERE id=? AND tenant_id=?',(vehicle_id,current['tenant_id'])).fetchone(): raise HTTPException(404,'Vehicle not found')
        last=db.execute('SELECT filled_on,odometer_km FROM fuel_logs WHERE vehicle_id=? AND tenant_id=? ORDER BY filled_on DESC,odometer_km DESC LIMIT 1',(vehicle_id,current['tenant_id'])).fetchone()
        if last and (body.filled_on.isoformat()<last['filled_on'] or body.odometer_km<=last['odometer_km']): raise HTTPException(422,'Fuel log must not predate the last log and odometer must increase')
        try: lid=db.execute('INSERT INTO fuel_logs(tenant_id,vehicle_id,filled_on,odometer_km,litres,cost_cents,driver,note) VALUES(?,?,?,?,?,?,?,?)',(current['tenant_id'],vehicle_id,body.filled_on.isoformat(),body.odometer_km,body.litres,body.cost_cents,body.driver.strip(),body.note.strip())).lastrowid
        except sqlite3.IntegrityError: raise HTTPException(409,'Fuel log already exists')
    return {'id':lid}


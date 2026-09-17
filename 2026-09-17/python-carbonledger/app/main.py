from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
import jwt
from dotenv import load_dotenv
from fastapi import Depends,FastAPI,Header,HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel,EmailStr,Field,field_validator
from .db import connect,init_db
from .security import decode,hash_password,issue,verify_password
load_dotenv();CATEGORIES={'energy','travel','freight','materials','waste','other'}
@asynccontextmanager
async def lifespan(_:FastAPI):init_db();yield
app=FastAPI(title='CarbonLedger',lifespan=lifespan)
class Register(BaseModel):organization:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128);annual_target_kg:float=Field(default=0,ge=0,le=1_000_000_000)
class Login(BaseModel):email:EmailStr;password:str
class ActivityIn(BaseModel):
    activity_date:date;category:str;source:str=Field(min_length=2,max_length=120);quantity:float=Field(gt=0,le=1_000_000_000);unit:str=Field(min_length=1,max_length=30);factor:float=Field(gt=0,le=1_000_000);notes:str=Field(default='',max_length=2000)
    @field_validator('category')
    @classmethod
    def category_ok(cls,v):
        if v not in CATEGORIES:raise ValueError('invalid category')
        return v
class TargetIn(BaseModel):annual_target_kg:float=Field(ge=0,le=1_000_000_000)
def user(authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Missing bearer token')
    try:p=decode(authorization[7:]);return {'id':int(p['sub']),'tenant_id':int(p['tenant_id'])}
    except (jwt.PyJWTError,KeyError,ValueError):raise HTTPException(401,'Invalid or expired token')
def one(i,tid):
    with connect() as db:r=db.execute('SELECT * FROM activities WHERE id=? AND tenant_id=?',(i,tid)).fetchone()
    if not r:raise HTTPException(404,'Activity not found')
    return dict(r)
@app.get('/',include_in_schema=False)
def index():return FileResponse(Path(__file__).parent/'static'/'index.html')
@app.get('/health')
def health():return {'status':'ok'}
@app.post('/api/auth/register',status_code=201)
def register(x:Register):
    with connect() as db:
        if db.execute('SELECT 1 FROM users WHERE lower(email)=lower(?)',(str(x.email),)).fetchone():raise HTTPException(409,'Email already registered')
        tid=db.execute('INSERT INTO tenants(name,target_kg) VALUES(?,?)',(x.organization.strip(),x.annual_target_kg)).lastrowid;uid=db.execute('INSERT INTO users(tenant_id,email,password_hash) VALUES(?,?,?)',(tid,str(x.email).lower(),hash_password(x.password))).lastrowid
    return {'access_token':issue(uid,tid),'token_type':'bearer'}
@app.post('/api/auth/login')
def login(x:Login):
    with connect() as db:u=db.execute('SELECT * FROM users WHERE lower(email)=lower(?)',(str(x.email),)).fetchone()
    if not u or not verify_password(x.password,u['password_hash']):raise HTTPException(401,'Invalid email or password')
    return {'access_token':issue(u['id'],u['tenant_id']),'token_type':'bearer'}
@app.get('/api/activities')
def activities(current=Depends(user)):
    with connect() as db:rows=db.execute('SELECT * FROM activities WHERE tenant_id=? ORDER BY activity_date DESC',(current['tenant_id'],)).fetchall()
    return [dict(r) for r in rows]
@app.post('/api/activities',status_code=201)
def create(x:ActivityIn,current=Depends(user)):
    total=round(x.quantity*x.factor,4)
    with connect() as db:i=db.execute('INSERT INTO activities(tenant_id,activity_date,category,source,quantity,unit,factor,kg_co2e,notes) VALUES(?,?,?,?,?,?,?,?,?)',(current['tenant_id'],x.activity_date.isoformat(),x.category,x.source.strip(),x.quantity,x.unit.strip(),x.factor,total,x.notes.strip())).lastrowid
    return one(i,current['tenant_id'])
@app.delete('/api/activities/{activity_id}',status_code=204)
def delete(activity_id:int,current=Depends(user)):
    one(activity_id,current['tenant_id'])
    with connect() as db:db.execute('DELETE FROM activities WHERE id=? AND tenant_id=?',(activity_id,current['tenant_id']))
@app.put('/api/target')
def target(x:TargetIn,current=Depends(user)):
    with connect() as db:db.execute('UPDATE tenants SET target_kg=? WHERE id=?',(x.annual_target_kg,current['tenant_id']))
    return {'annual_target_kg':x.annual_target_kg}
@app.get('/api/dashboard')
def dashboard(year:int|None=None,current=Depends(user)):
    year=year or date.today().year
    with connect() as db:
        rows=db.execute("SELECT category,SUM(kg_co2e) total FROM activities WHERE tenant_id=? AND substr(activity_date,1,4)=? GROUP BY category",(current['tenant_id'],str(year))).fetchall();tenant=db.execute('SELECT target_kg FROM tenants WHERE id=?',(current['tenant_id'],)).fetchone()
    by_category={r['category']:round(r['total'],2) for r in rows};total=round(sum(by_category.values()),2);target_kg=tenant['target_kg']
    return {'year':year,'total_kg_co2e':total,'target_kg':target_kg,'remaining_kg':round(max(0,target_kg-total),2),'by_category':by_category}


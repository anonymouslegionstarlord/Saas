from contextlib import asynccontextmanager
from datetime import datetime,timezone
from pathlib import Path
import jwt
from dotenv import load_dotenv
from fastapi import Depends,FastAPI,Header,HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel,EmailStr,Field,field_validator,model_validator
from .db import connect,init_db
from .security import decode,hash_password,token,verify_password
load_dotenv();PRIORITIES={'low','medium','high','urgent'};STATES={'open','in_progress','resolved','closed'}
@asynccontextmanager
async def lifespan(_:FastAPI):init_db();yield
app=FastAPI(title='SLAClock',lifespan=lifespan)
class Register(BaseModel):organization:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel):email:EmailStr;password:str
class TicketIn(BaseModel):
    subject:str=Field(min_length=3,max_length=160);customer:str=Field(min_length=2,max_length=100);assignee:str=Field(min_length=2,max_length=100);priority:str;status:str='open';opened_at:datetime;due_at:datetime;description:str=Field(default='',max_length=3000)
    @field_validator('priority')
    @classmethod
    def priority_ok(cls,v):
        if v not in PRIORITIES:raise ValueError('invalid priority')
        return v
    @field_validator('status')
    @classmethod
    def status_ok(cls,v):
        if v not in STATES:raise ValueError('invalid status')
        return v
    @model_validator(mode='after')
    def due_ok(self):
        if self.due_at<=self.opened_at:raise ValueError('due_at must be after opened_at')
        return self
class StatusIn(BaseModel):status:str
def iso(dt):return dt.astimezone(timezone.utc).isoformat()
def user(authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Missing bearer token')
    try:p=decode(authorization[7:]);return {'id':int(p['sub']),'tenant_id':int(p['tenant_id'])}
    except (jwt.PyJWTError,KeyError,ValueError):raise HTTPException(401,'Invalid or expired token')
def one(i,tid):
    with connect() as db:r=db.execute('SELECT * FROM tickets WHERE id=? AND tenant_id=?',(i,tid)).fetchone()
    if not r:raise HTTPException(404,'Ticket not found')
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
    return {'access_token':token(uid,tid),'token_type':'bearer'}
@app.post('/api/auth/login')
def login(x:Login):
    with connect() as db:u=db.execute('SELECT * FROM users WHERE lower(email)=lower(?)',(str(x.email),)).fetchone()
    if not u or not verify_password(x.password,u['password_hash']):raise HTTPException(401,'Invalid email or password')
    return {'access_token':token(u['id'],u['tenant_id']),'token_type':'bearer'}
@app.get('/api/tickets')
def tickets(current=Depends(user)):
    with connect() as db:rows=db.execute('SELECT * FROM tickets WHERE tenant_id=? ORDER BY due_at',(current['tenant_id'],)).fetchall()
    return [dict(r) for r in rows]
@app.post('/api/tickets',status_code=201)
def create(x:TicketIn,current=Depends(user)):
    with connect() as db:i=db.execute('INSERT INTO tickets(tenant_id,subject,customer,assignee,priority,status,opened_at,due_at,description) VALUES(?,?,?,?,?,?,?,?,?)',(current['tenant_id'],x.subject.strip(),x.customer.strip(),x.assignee.strip(),x.priority,x.status,iso(x.opened_at),iso(x.due_at),x.description.strip())).lastrowid
    return one(i,current['tenant_id'])
@app.patch('/api/tickets/{ticket_id}/status')
def change(ticket_id:int,x:StatusIn,current=Depends(user)):
    if x.status not in STATES:raise HTTPException(422,'Invalid status')
    one(ticket_id,current['tenant_id']);resolved=iso(datetime.now(timezone.utc)) if x.status=='resolved' else None
    with connect() as db:db.execute('UPDATE tickets SET status=?,resolved_at=? WHERE id=? AND tenant_id=?',(x.status,resolved,ticket_id,current['tenant_id']))
    return one(ticket_id,current['tenant_id'])
@app.delete('/api/tickets/{ticket_id}',status_code=204)
def delete(ticket_id:int,current=Depends(user)):
    one(ticket_id,current['tenant_id'])
    with connect() as db:db.execute('DELETE FROM tickets WHERE id=? AND tenant_id=?',(ticket_id,current['tenant_id']))
@app.get('/api/dashboard')
def dashboard(current=Depends(user)):
    now=datetime.now(timezone.utc).isoformat()
    with connect() as db:r=db.execute("SELECT COUNT(*) total,SUM(CASE WHEN status IN ('open','in_progress') THEN 1 ELSE 0 END) active,SUM(CASE WHEN status IN ('open','in_progress') AND due_at < ? THEN 1 ELSE 0 END) breached,SUM(CASE WHEN status='resolved' AND resolved_at <= due_at THEN 1 ELSE 0 END) within_sla FROM tickets WHERE tenant_id=?",(now,current['tenant_id'])).fetchone()
    d=dict(r);return {k:(v or 0) for k,v in d.items()}


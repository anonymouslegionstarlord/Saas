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
app=FastAPI(title=os.getenv("APP_NAME","ExpenseGate"),lifespan=lifespan)
class Register(BaseModel): name:str=Field(min_length=2,max_length=80);workspace:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=8,max_length=128)
class Login(BaseModel): email:EmailStr;password:str
class ExpenseIn(BaseModel):
    merchant:str=Field(min_length=2,max_length=120);category:str;amount_cents:int=Field(gt=0,le=1000000000);incurred_on:date;description:str=Field(default='',max_length=1000)
    @field_validator('category')
    @classmethod
    def category_value(cls,v):
        if v not in {'travel','meals','software','office','other'}: raise ValueError('invalid category')
        return v
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
    with connect() as db: expenses=[dict(x) for x in db.execute('SELECT * FROM expenses WHERE tenant_id=? ORDER BY incurred_on DESC,created_at DESC',(current['tenant_id'],))]
    total=lambda status:sum(x['amount_cents'] for x in expenses if x['status']==status)
    return {'expenses':expenses,'summary':{'submitted_cents':total('submitted'),'approved_cents':total('approved'),'rejected_cents':total('rejected'),'awaiting_review':sum(x['status']=='submitted' for x in expenses)}}
@app.post('/api/expenses',status_code=201)
def add_expense(body:ExpenseIn,current=Depends(user)):
    with connect() as db: eid=db.execute('INSERT INTO expenses(tenant_id,merchant,category,amount_cents,incurred_on,description) VALUES(?,?,?,?,?,?)',(current['tenant_id'],body.merchant.strip(),body.category,body.amount_cents,body.incurred_on.isoformat(),body.description.strip())).lastrowid
    return {'id':eid,'status':'submitted'}
@app.patch('/api/expenses/{expense_id}/review')
def review(expense_id:int,body:ReviewIn,current=Depends(user)):
    with connect() as db:
        row=db.execute('SELECT status FROM expenses WHERE id=? AND tenant_id=?',(expense_id,current['tenant_id'])).fetchone()
        if not row: raise HTTPException(404,'Expense not found')
        if row['status']!='submitted': raise HTTPException(409,'Expense has already been reviewed')
        db.execute('UPDATE expenses SET status=?,review_note=?,reviewed_at=CURRENT_TIMESTAMP WHERE id=? AND tenant_id=?',(body.status,body.review_note.strip(),expense_id,current['tenant_id']))
    return {'status':body.status}


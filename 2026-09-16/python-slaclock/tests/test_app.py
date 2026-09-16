from datetime import datetime,timedelta,timezone
from fastapi.testclient import TestClient
from app.main import app
def auth(c,email,org):
    r=c.post('/api/auth/register',json={'organization':org,'email':email,'password':'strong-pass-123'});return {'Authorization':f"Bearer {r.json()['access_token']}"}
def payload(hours=1):
    now=datetime.now(timezone.utc);return {'subject':'Login unavailable','customer':'Acme','assignee':'Ava','priority':'urgent','status':'open','opened_at':now.isoformat(),'due_at':(now+timedelta(hours=hours)).isoformat(),'description':'Users cannot sign in'}
def test_ticket_workflow_and_metrics(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL',str(tmp_path/'one.db'))
    with TestClient(app) as c:
        h=auth(c,'one@example.com','One');item=c.post('/api/tickets',headers=h,json=payload()).json();assert c.get('/api/dashboard',headers=h).json()['active']==1
        assert c.patch(f"/api/tickets/{item['id']}/status",headers=h,json={'status':'resolved'}).status_code==200
        assert c.get('/api/dashboard',headers=h).json()['within_sla']==1
def test_validation_and_tenant_isolation(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL',str(tmp_path/'two.db'))
    with TestClient(app) as c:
        a=auth(c,'a@example.com','Alpha');b=auth(c,'b@example.com','Beta');item=c.post('/api/tickets',headers=a,json=payload()).json()
        assert c.get('/api/tickets',headers=b).json()==[];assert c.delete(f"/api/tickets/{item['id']}",headers=b).status_code==404
        bad=payload();bad['due_at']=bad['opened_at'];assert c.post('/api/tickets',headers=a,json=bad).status_code==422

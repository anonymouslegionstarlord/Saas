from datetime import date,timedelta
from fastapi.testclient import TestClient
from app.main import app

def register(client,email,org):
    r=client.post('/api/auth/register',json={'organization':org,'email':email,'password':'strong-pass-123'}); assert r.status_code==201
    return {'Authorization':f"Bearer {r.json()['access_token']}"}
def test_workflow_and_metrics(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL',str(tmp_path/'one.db'))
    with TestClient(app) as c:
        h=register(c,'owner@example.com','Acme'); meeting=c.post('/api/meetings',headers=h,json={'title':'Planning','held_on':date.today().isoformat(),'facilitator':'Ada','notes':'Q4'}).json()
        action=c.post('/api/decisions',headers=h,json={'meeting_id':meeting['id'],'summary':'Launch beta','owner':'Sam','due_date':(date.today()-timedelta(days=1)).isoformat(),'status':'open'}); assert action.status_code==201
        assert c.get('/api/dashboard',headers=h).json()=={'total':1,'completed':0,'overdue':1}
        assert c.patch(f"/api/decisions/{action.json()['id']}/status?status=done",headers=h).status_code==200
        assert c.get('/api/dashboard',headers=h).json()['completed']==1
def test_validation_and_isolation(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL',str(tmp_path/'two.db'))
    with TestClient(app) as c:
        a=register(c,'a@example.com','A Team'); b=register(c,'b@example.com','B Team')
        meeting=c.post('/api/meetings',headers=a,json={'title':'Review','held_on':date.today().isoformat(),'facilitator':'Ava'}).json()
        assert c.post('/api/decisions',headers=b,json={'meeting_id':meeting['id'],'summary':'Hidden decision','owner':'Ben'}).status_code==404
        assert c.get('/api/meetings',headers=b).json()==[]
        assert c.post('/api/meetings',headers=a,json={'title':'x','held_on':'invalid','facilitator':'a'}).status_code==422


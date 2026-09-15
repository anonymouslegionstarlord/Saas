from datetime import date,timedelta
from fastapi.testclient import TestClient
from app.main import app
def auth(c,email,org):
    r=c.post('/api/auth/register',json={'organization':org,'email':email,'password':'strong-pass-123'});return {'Authorization':f"Bearer {r.json()['access_token']}"}
def payload():return {'name':'New onboarding','hypothesis':'Shorter signup improves activation','primary_metric':'Activation rate','target_lift':8,'starts_on':date.today().isoformat(),'ends_on':(date.today()+timedelta(days=14)).isoformat(),'status':'running','notes':''}
def test_experiment_result_and_metrics(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL',str(tmp_path/'one.db'))
    with TestClient(app) as c:
        h=auth(c,'one@example.com','Lab One');r=c.post('/api/experiments',headers=h,json=payload());assert r.status_code==201
        done=c.patch(f"/api/experiments/{r.json()['id']}/result",headers=h,json={'status':'won','baseline':20,'observed':24,'notes':'Significant'});assert done.status_code==200
        assert c.get('/api/dashboard',headers=h).json()=={'total':1,'running':0,'wins':1,'average_lift':20.0}
def test_validation_and_tenant_isolation(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL',str(tmp_path/'two.db'))
    with TestClient(app) as c:
        a=auth(c,'a@example.com','Alpha');b=auth(c,'b@example.com','Beta');item=c.post('/api/experiments',headers=a,json=payload()).json()
        assert c.get('/api/experiments',headers=b).json()==[]
        assert c.delete(f"/api/experiments/{item['id']}",headers=b).status_code==404
        bad=payload()|{'ends_on':date.today().isoformat()};assert c.post('/api/experiments',headers=a,json=bad).status_code==422


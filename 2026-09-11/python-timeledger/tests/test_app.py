import importlib
from fastapi.testclient import TestClient
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'test.db'));monkeypatch.setenv('JWT_SECRET','test')
    from app import main
    importlib.reload(main);return TestClient(main.app)
def signup(c,email,workspace):
    r=c.post('/api/auth/register',json={'name':'Owner','workspace':workspace,'email':email,'password':'password1'});return {'Authorization':'Bearer '+r.json()['token']}
def project(c,h): return c.post('/api/projects',headers=h,json={'name':'Portal rebuild','client':'Acme','hourly_rate_cents':150000,'budget_hours':100}).json()['id']
def test_approval_billable_value_and_repeat_guard(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        h=signup(c,'one@example.com','Studio');pid=project(c,h);item=c.post(f'/api/projects/{pid}/entries',headers=h,json={'worked_on':'2026-09-11','hours':2.5,'task':'API implementation','billable':True}).json();assert c.patch(f"/api/entries/{item['id']}/review",headers=h,json={'status':'approved','review_note':'Work confirmed'}).status_code==200
        d=c.get('/api/dashboard',headers=h).json();assert d['summary']['approved_hours']==2.5 and d['summary']['approved_billable_cents']==375000
        assert c.patch(f"/api/entries/{item['id']}/review",headers=h,json={'status':'rejected','review_note':'Second decision'}).status_code==409
def test_tenant_isolation_and_hours_validation(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        x=signup(c,'x@example.com','Alpha');y=signup(c,'y@example.com','Beta');pid=project(c,x)
        body={'worked_on':'2026-09-11','hours':2,'task':'Private work','billable':True};assert c.post(f'/api/projects/{pid}/entries',headers=y,json=body).status_code==404
        body['hours']=25;assert c.post(f'/api/projects/{pid}/entries',headers=x,json=body).status_code==422


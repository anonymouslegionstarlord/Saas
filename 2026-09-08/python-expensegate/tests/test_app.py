import importlib
from fastapi.testclient import TestClient
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'test.db'));monkeypatch.setenv('JWT_SECRET','test')
    from app import main
    importlib.reload(main);return TestClient(main.app)
def signup(c,email,workspace):
    r=c.post('/api/auth/register',json={'name':'Owner','workspace':workspace,'email':email,'password':'password1'});return {'Authorization':'Bearer '+r.json()['token']}
def expense(): return {'merchant':'Cloud Tools','category':'software','amount_cents':129900,'incurred_on':'2026-09-08','description':'Annual team subscription'}
def test_expense_approval_and_metrics(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        h=signup(c,'one@example.com','Acme');item=c.post('/api/expenses',headers=h,json=expense()).json()
        assert c.patch('/api/expenses/'+str(item['id'])+'/review',headers=h,json={'status':'approved','review_note':'Receipt and budget verified'}).status_code==200
        data=c.get('/api/dashboard',headers=h).json();assert data['summary']['approved_cents']==129900 and data['summary']['awaiting_review']==0
        assert c.patch('/api/expenses/'+str(item['id'])+'/review',headers=h,json={'status':'rejected','review_note':'Second review'}).status_code==409
def test_tenant_isolation_and_validation(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        x=signup(c,'x@example.com','Alpha');y=signup(c,'y@example.com','Beta');item=c.post('/api/expenses',headers=x,json=expense()).json()
        assert c.patch('/api/expenses/'+str(item['id'])+'/review',headers=y,json={'status':'approved','review_note':'Should not work'}).status_code==404
        bad=expense();bad['amount_cents']=0;assert c.post('/api/expenses',headers=x,json=bad).status_code==422


import importlib
from fastapi.testclient import TestClient
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'test.db'));monkeypatch.setenv('JWT_SECRET','test')
    from app import main
    importlib.reload(main);return TestClient(main.app)
def signup(c,email,workspace):
    r=c.post('/api/auth/register',json={'name':'Owner','workspace':workspace,'email':email,'password':'password1'});return {'Authorization':'Bearer '+r.json()['token']}
def vehicle(c,h): return c.post('/api/vehicles',headers=h,json={'registration':'DL 01 AB 1234','label':'Delivery van','fuel_type':'diesel','efficiency_floor':12}).json()['id']
def log(day,odo,litres=10): return {'filled_on':day,'odometer_km':odo,'litres':litres,'cost_cents':90000,'driver':'Riya'}
def test_efficiency_cost_and_low_alert(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        h=signup(c,'one@example.com','Acme');vid=vehicle(c,h);assert c.post(f'/api/vehicles/{vid}/fuel-logs',headers=h,json=log('2026-09-01',1000)).status_code==201;assert c.post(f'/api/vehicles/{vid}/fuel-logs',headers=h,json=log('2026-09-05',1100)).status_code==201
        d=c.get('/api/dashboard',headers=h).json();assert d['vehicles'][0]['latest_efficiency']==10 and d['summary']=={'vehicles':1,'low_efficiency':1,'total_cost_cents':180000}
def test_tenant_isolation_and_odometer_validation(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        x=signup(c,'x@example.com','Alpha');y=signup(c,'y@example.com','Beta');vid=vehicle(c,x)
        assert c.post(f'/api/vehicles/{vid}/fuel-logs',headers=y,json=log('2026-09-01',1000)).status_code==404
        assert c.post(f'/api/vehicles/{vid}/fuel-logs',headers=x,json=log('2026-09-01',1000)).status_code==201
        assert c.post(f'/api/vehicles/{vid}/fuel-logs',headers=x,json=log('2026-09-02',999)).status_code==422


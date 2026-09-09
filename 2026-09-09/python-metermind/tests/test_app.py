import importlib
from fastapi.testclient import TestClient
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'test.db'));monkeypatch.setenv('JWT_SECRET','test')
    from app import main
    importlib.reload(main);return TestClient(main.app)
def signup(c,email,workspace):
    r=c.post('/api/auth/register',json={'name':'Owner','workspace':workspace,'email':email,'password':'password1'});return {'Authorization':'Bearer '+r.json()['token']}
def meter(c,h): return c.post('/api/meters',headers=h,json={'name':'Main supply','location':'Delhi office','unit':'kWh','alert_percent':25}).json()['id']
def test_usage_and_anomaly_detection(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        h=signup(c,'one@example.com','Acme');mid=meter(c,h)
        for day,value in [('2026-09-01',100),('2026-09-02',120),('2026-09-03',160)]: assert c.post(f'/api/meters/{mid}/readings',headers=h,json={'reading_on':day,'value':value}).status_code==201
        d=c.get('/api/dashboard',headers=h).json();assert d['summary']['anomalies']==1 and d['meters'][0]['latest_usage']==40
def test_tenant_isolation_and_monotonic_validation(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        x=signup(c,'x@example.com','Alpha');y=signup(c,'y@example.com','Beta');mid=meter(c,x)
        assert c.post(f'/api/meters/{mid}/readings',headers=y,json={'reading_on':'2026-09-01','value':10}).status_code==404
        assert c.post(f'/api/meters/{mid}/readings',headers=x,json={'reading_on':'2026-09-02','value':100}).status_code==201
        assert c.post(f'/api/meters/{mid}/readings',headers=x,json={'reading_on':'2026-09-03','value':90}).status_code==422


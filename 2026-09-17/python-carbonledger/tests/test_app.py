from datetime import date
from fastapi.testclient import TestClient
from app.main import app
def auth(c,email,org,target=1000):
    r=c.post('/api/auth/register',json={'organization':org,'email':email,'password':'strong-pass-123','annual_target_kg':target});return {'Authorization':f"Bearer {r.json()['access_token']}"}
def activity():return {'activity_date':date.today().isoformat(),'category':'energy','source':'Office electricity','quantity':100,'unit':'kWh','factor':0.4,'notes':'Utility statement'}
def test_emission_calculation_and_dashboard(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL',str(tmp_path/'one.db'))
    with TestClient(app) as c:
        h=auth(c,'one@example.com','One');r=c.post('/api/activities',headers=h,json=activity());assert r.status_code==201 and r.json()['kg_co2e']==40
        assert c.get('/api/dashboard',headers=h).json()=={'year':date.today().year,'total_kg_co2e':40.0,'target_kg':1000.0,'remaining_kg':960.0,'by_category':{'energy':40.0}}
def test_validation_and_isolation(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_URL',str(tmp_path/'two.db'))
    with TestClient(app) as c:
        a=auth(c,'a@example.com','Alpha');b=auth(c,'b@example.com','Beta');item=c.post('/api/activities',headers=a,json=activity()).json()
        assert c.get('/api/activities',headers=b).json()==[];assert c.delete(f"/api/activities/{item['id']}",headers=b).status_code==404
        assert c.post('/api/activities',headers=a,json=activity()|{'category':'unknown'}).status_code==422


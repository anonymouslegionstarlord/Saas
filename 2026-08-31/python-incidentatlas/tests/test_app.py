import importlib
from fastapi.testclient import TestClient
def test_incident_flow_and_isolation(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"incidents.db"));monkeypatch.setenv("APP_SECRET","test-secret")
    import app.main
    importlib.reload(app.main);client=TestClient(app.main.app)
    one=client.post("/api/auth/register",json={"workspace":"North","name":"Nora","email":"nora@example.com","password":"password1"}).json();two=client.post("/api/auth/register",json={"workspace":"South","name":"Sam","email":"sam@example.com","password":"password2"}).json()
    h1={"Authorization":"Bearer "+one["access_token"]};h2={"Authorization":"Bearer "+two["access_token"]}
    incident=client.post("/api/incidents",headers=h1,json={"title":"API latency","severity":"major","summary":"Requests are responding too slowly."}).json()
    assert client.get("/api/incidents",headers=h2).json()==[]
    assert client.post("/api/incidents/"+str(incident["id"])+"/updates",headers=h2,json={"status":"resolved","message":"Not owned"}).status_code==404
    assert client.post("/api/incidents/"+str(incident["id"])+"/updates",headers=h1,json={"status":"resolved","message":"Latency returned to normal."}).status_code==201
    key=client.get("/api/me",headers=h1).json()["status_key"];public=client.get("/api/public/status/"+key).json()
    assert public["workspace"]=="North" and public["incidents"][0]["status"]=="resolved"
def test_validation_and_unknown_status_page(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"invalid.db"))
    import app.main
    importlib.reload(app.main);client=TestClient(app.main.app)
    user=client.post("/api/auth/register",json={"workspace":"Valid","name":"Owner","email":"o@example.com","password":"password1"}).json();h={"Authorization":"Bearer "+user["access_token"]}
    assert client.post("/api/incidents",headers=h,json={"title":"x","severity":"extreme","summary":"short"}).status_code==422
    assert client.get("/api/public/status/missing").status_code==404

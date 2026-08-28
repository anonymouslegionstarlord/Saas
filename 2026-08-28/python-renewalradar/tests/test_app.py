import importlib
from fastapi.testclient import TestClient

def test_subscription_flow_and_isolation(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"renewals.db"))
    monkeypatch.setenv("APP_SECRET","test-secret")
    import app.main
    importlib.reload(app.main)
    client=TestClient(app.main.app)
    one=client.post("/api/auth/register",json={"workspace":"North","name":"Nora","email":"nora@example.com","password":"password1"}).json()
    two=client.post("/api/auth/register",json={"workspace":"South","name":"Sam","email":"sam@example.com","password":"password2"}).json()
    h1={"Authorization":"Bearer "+one["access_token"]};h2={"Authorization":"Bearer "+two["access_token"]}
    item=client.post("/api/subscriptions",headers=h1,json={"vendor":"CloudBox","category":"Infrastructure","cost":25,"billing_cycle":"monthly","renewal_date":"2030-01-01","owner":"Nora","notes":"Core"}).json()
    assert len(client.get("/api/subscriptions",headers=h1).json())==1
    assert client.get("/api/subscriptions",headers=h2).json()==[]
    assert client.patch("/api/subscriptions/"+str(item["id"]),headers=h2,json={"active":False}).status_code==404
    assert client.get("/api/summary",headers=h1).json()["annual_spend"]==300

def test_validation(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"invalid.db"))
    import app.main
    importlib.reload(app.main)
    client=TestClient(app.main.app)
    token=client.post("/api/auth/register",json={"workspace":"Valid","name":"Owner","email":"o@example.com","password":"password1"}).json()["access_token"]
    response=client.post("/api/subscriptions",headers={"Authorization":"Bearer "+token},json={"vendor":"X","category":"Y","cost":-1,"billing_cycle":"weekly","renewal_date":"bad","owner":"Z"})
    assert response.status_code==422

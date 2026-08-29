import importlib
from fastapi.testclient import TestClient
def test_acknowledgement_and_tenant_isolation(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"policies.db"));monkeypatch.setenv("APP_SECRET","test-secret")
    import app.main
    importlib.reload(app.main);client=TestClient(app.main.app)
    one=client.post("/api/auth/register",json={"workspace":"North","name":"Nora","email":"nora@example.com","password":"password1"}).json()
    two=client.post("/api/auth/register",json={"workspace":"South","name":"Sam","email":"sam@example.com","password":"password2"}).json()
    h1={"Authorization":"Bearer "+one["access_token"]};h2={"Authorization":"Bearer "+two["access_token"]}
    policy=client.post("/api/policies",headers=h1,json={"title":"Remote work","version":"1.0","content":"Employees must protect company information while working remotely."}).json()
    assert client.get("/api/public/policies/"+policy["public_key"]).status_code==200
    assert client.post("/api/public/policies/"+policy["public_key"]+"/acknowledge",json={"employee_name":"Alex","employee_email":"alex@example.com","accepted":True}).status_code==201
    assert len(client.get("/api/policies/"+str(policy["id"])+"/acknowledgements",headers=h1).json())==1
    assert client.get("/api/policies/"+str(policy["id"])+"/acknowledgements",headers=h2).status_code==404
def test_acceptance_and_duplicate_validation(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"validation.db"))
    import app.main
    importlib.reload(app.main);client=TestClient(app.main.app)
    user=client.post("/api/auth/register",json={"workspace":"Valid","name":"Owner","email":"o@example.com","password":"password1"}).json();h={"Authorization":"Bearer "+user["access_token"]}
    policy=client.post("/api/policies",headers=h,json={"title":"Security","version":"1","content":"This security policy has enough content for publishing."}).json();url="/api/public/policies/"+policy["public_key"]+"/acknowledge"
    assert client.post(url,json={"employee_name":"Alex","employee_email":"a@example.com","accepted":False}).status_code==422
    assert client.post(url,json={"employee_name":"Alex","employee_email":"a@example.com","accepted":True}).status_code==201
    assert client.post(url,json={"employee_name":"Alex","employee_email":"a@example.com","accepted":True}).status_code==409

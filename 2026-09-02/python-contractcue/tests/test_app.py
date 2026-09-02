import importlib
from fastapi.testclient import TestClient

def make_client(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"test.db")); monkeypatch.setenv("JWT_SECRET","test-secret")
    from app import main
    importlib.reload(main)
    return TestClient(main.app)

def signup(client,email,workspace):
    r=client.post("/api/auth/register",json={"name":"Owner","workspace":workspace,"email":email,"password":"password1"})
    return {"Authorization":"Bearer "+r.json()["token"]}

def payload(title="MSA"):
    return {"title":title,"counterparty":"Northstar","owner_email":"legal@example.com","starts_on":"2026-09-01","ends_on":"2027-08-31","value_cents":1200000,"notes":"Annual renewal"}

def test_contract_and_obligation_workflow(tmp_path,monkeypatch):
    with make_client(tmp_path,monkeypatch) as c:
        h=signup(c,"owner@example.com","Acme")
        contract=c.post("/api/contracts",headers=h,json=payload()).json()
        obligation=c.post(f"/api/contracts/{contract['id']}/obligations",headers=h,json={"title":"Deliver security report","due_on":"2026-09-10","assignee":"Legal"})
        assert obligation.status_code==201
        assert c.patch(f"/api/obligations/{obligation.json()['id']}?status_value=done",headers=h).json()["status"]=="done"
        assert c.get("/api/dashboard",headers=h).json()["summary"]["total"]==1

def test_validation_and_tenant_isolation(tmp_path,monkeypatch):
    with make_client(tmp_path,monkeypatch) as c:
        first=signup(c,"first@example.com","First"); second=signup(c,"second@example.com","Second")
        contract=c.post("/api/contracts",headers=first,json=payload("Private")).json()
        assert c.post(f"/api/contracts/{contract['id']}/obligations",headers=second,json={"title":"Secret task","due_on":"2026-09-10","assignee":"Sam"}).status_code==404
        bad=payload("Bad"); bad["ends_on"]="2025-01-01"
        assert c.post("/api/contracts",headers=first,json=bad).status_code==422

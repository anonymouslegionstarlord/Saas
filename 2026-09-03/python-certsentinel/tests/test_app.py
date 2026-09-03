import importlib
from fastapi.testclient import TestClient
def make_client(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"test.db"));monkeypatch.setenv("JWT_SECRET","test-secret")
    from app import main
    importlib.reload(main);return TestClient(main.app)
def signup(c,email,workspace):
    r=c.post("/api/auth/register",json={"name":"Owner","workspace":workspace,"email":email,"password":"password1"})
    return {"Authorization":"Bearer "+r.json()["token"]}
def test_credential_workflow(tmp_path,monkeypatch):
    with make_client(tmp_path,monkeypatch) as c:
        h=signup(c,"one@example.com","Acme");p=c.post("/api/people",headers=h,json={"name":"Mira","email":"mira@example.com","department":"Security"}).json()
        credential=c.post("/api/people/"+str(p["id"])+"/credentials",headers=h,json={"certification":"CCNA","issuer":"Cisco","credential_code":"DEV-1","issued_on":"2026-01-01","expires_on":"2027-01-01","notes":"Annual check"})
        assert credential.status_code==201
        assert c.patch("/api/credentials/"+str(credential.json()["id"])+"?status_value=renewing",headers=h).json()["status"]=="renewing"
        assert c.get("/api/dashboard",headers=h).json()["summary"]["total"]==1
def test_validation_and_tenant_isolation(tmp_path,monkeypatch):
    with make_client(tmp_path,monkeypatch) as c:
        first=signup(c,"first@example.com","First");second=signup(c,"second@example.com","Second")
        p=c.post("/api/people",headers=first,json={"name":"Private User","email":"private@example.com","department":"Ops"}).json()
        body={"certification":"AWS","issuer":"Amazon","issued_on":"2026-01-01","expires_on":"2027-01-01"}
        assert c.post("/api/people/"+str(p["id"])+"/credentials",headers=second,json=body).status_code==404
        body["expires_on"]="2025-01-01"
        assert c.post("/api/people/"+str(p["id"])+"/credentials",headers=first,json=body).status_code==422

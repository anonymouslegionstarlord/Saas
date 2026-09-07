import importlib
from fastapi.testclient import TestClient
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"test.db"));monkeypatch.setenv("JWT_SECRET","test")
    from app import main
    importlib.reload(main);return TestClient(main.app)
def signup(c,email,workspace):
    r=c.post("/api/auth/register",json={"name":"Owner","workspace":workspace,"email":email,"password":"password1"});return {"Authorization":"Bearer "+r.json()["token"]}
def audit():
    return {"title":"Q3 security audit","area":"Identity","lead":"Mira","starts_on":"2026-09-01","ends_on":"2026-09-30"}
def test_finding_remediation(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        h=signup(c,"one@example.com","Acme");a=c.post("/api/audits",headers=h,json=audit()).json();f=c.post("/api/audits/"+str(a["id"])+"/findings",headers=h,json={"title":"Dormant administrator accounts","severity":"critical","owner":"IT","due_on":"2026-09-20"}).json()
        assert c.patch("/api/findings/"+str(f["id"]),headers=h,json={"status":"verified","remediation":"Accounts removed and evidence reviewed"}).status_code==200
        assert c.get("/api/dashboard",headers=h).json()["summary"]["critical"]==0
def test_tenant_isolation_and_validation(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        x=signup(c,"x@example.com","Alpha");y=signup(c,"y@example.com","Beta");a=c.post("/api/audits",headers=x,json=audit()).json()
        assert c.post("/api/audits/"+str(a["id"])+"/findings",headers=y,json={"title":"Private finding","severity":"high","owner":"IT","due_on":"2026-09-20"}).status_code==404
        bad=audit();bad["ends_on"]="2025-01-01";assert c.post("/api/audits",headers=x,json=bad).status_code==422

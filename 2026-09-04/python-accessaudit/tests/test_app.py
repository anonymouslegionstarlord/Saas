import importlib
from fastapi.testclient import TestClient
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"test.db"));monkeypatch.setenv("JWT_SECRET","test")
    from app import main
    importlib.reload(main);return TestClient(main.app)
def signup(c,email,name):
    r=c.post("/api/auth/register",json={"name":"Owner","workspace":name,"email":email,"password":"password1"})
    return {"Authorization":"Bearer "+r.json()["token"]}
def test_review_workflow(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        h=signup(c,"one@example.com","One");s=c.post("/api/systems",headers=h,json={"name":"GitHub","owner":"IT","risk":"high"}).json()
        g=c.post("/api/systems/"+str(s["id"])+"/grants",headers=h,json={"subject_email":"dev@example.com","role":"admin","review_due":"2026-09-30"}).json()
        assert c.patch("/api/grants/"+str(g["id"]),headers=h,json={"decision":"retain","justification":"Still owns deployment"}).status_code==200
        assert c.get("/api/dashboard",headers=h).json()["summary"]["pending"]==0
def test_tenant_isolation_and_validation(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        a=signup(c,"a@example.com","Alpha");b=signup(c,"b@example.com","Beta")
        s=c.post("/api/systems",headers=a,json={"name":"Payroll","owner":"IT","risk":"high"}).json()
        assert c.post("/api/systems/"+str(s["id"])+"/grants",headers=b,json={"subject_email":"x@example.com","role":"viewer","review_due":"2026-09-30"}).status_code==404
        assert c.post("/api/systems",headers=a,json={"name":"Bad","owner":"IT","risk":"critical"}).status_code==422

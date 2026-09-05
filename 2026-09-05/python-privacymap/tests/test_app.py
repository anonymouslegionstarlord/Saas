import importlib
from fastapi.testclient import TestClient
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"test.db"));monkeypatch.setenv("JWT_SECRET","test")
    from app import main
    importlib.reload(main);return TestClient(main.app)
def signup(c,email,workspace):
    r=c.post("/api/auth/register",json={"name":"Owner","workspace":workspace,"email":email,"password":"password1"});return {"Authorization":"Bearer "+r.json()["token"]}
def activity():
    return {"name":"Customer support","owner":"Privacy","purpose":"Resolve customer questions","lawful_basis":"contract","data_subjects":"Customers","retention_days":365,"review_due":"2026-10-01","risk":"medium"}
def test_processing_inventory(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        h=signup(c,"one@example.com","Acme");a=c.post("/api/activities",headers=h,json=activity()).json()
        assert c.post("/api/activities/"+str(a["id"])+"/data-items",headers=h,json={"category":"Email address","sensitive":False,"source":"Customer","recipient":"Support"}).status_code==201
        assert c.get("/api/dashboard",headers=h).json()["activities"][0]["data_item_count"]==1
def test_tenant_isolation_and_validation(tmp_path,monkeypatch):
    with client(tmp_path,monkeypatch) as c:
        a=signup(c,"a@example.com","Alpha");b=signup(c,"b@example.com","Beta");item=c.post("/api/activities",headers=a,json=activity()).json()
        assert c.post("/api/activities/"+str(item["id"])+"/data-items",headers=b,json={"category":"Address","source":"Form"}).status_code==404
        bad=activity();bad["lawful_basis"]="because"
        assert c.post("/api/activities",headers=a,json=bad).status_code==422

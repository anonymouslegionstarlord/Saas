import importlib

from fastapi.testclient import TestClient


def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db")); monkeypatch.setenv("JWT_SECRET", "test-secret")
    from app import main
    importlib.reload(main)
    return TestClient(main.app)


def register(c, email, workspace):
    response = c.post("/api/auth/register", json={"name":"Owner","email":email,"password":"password1","workspace":workspace})
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_vendor_workflow(tmp_path, monkeypatch):
    with client(tmp_path, monkeypatch) as c:
        headers = register(c, "one@example.com", "Acme")
        vendor = c.post("/api/vendors", headers=headers, json={"name":"CloudCo","service":"Hosting","owner_email":"ops@cloud.co","data_access":"confidential","criticality":"high","next_review":"2026-09-30","notes":"SOC 2 received"})
        assert vendor.status_code == 201
        assessed = c.post(f"/api/vendors/{vendor.json()['id']}/assessments", headers=headers, json={"security":4,"privacy":5,"resilience":3,"comment":"Reviewed"})
        assert assessed.json()["score"] == 4.0
        assert c.get("/api/dashboard", headers=headers).json()["summary"]["high"] == 1


def test_tenant_isolation_and_validation(tmp_path, monkeypatch):
    with client(tmp_path, monkeypatch) as c:
        first = register(c, "first@example.com", "First")
        second = register(c, "second@example.com", "Second")
        vendor = c.post("/api/vendors", headers=first, json={"name":"Private","service":"Payroll","owner_email":"a@b.com","data_access":"internal","criticality":"medium","next_review":"2026-10-01"}).json()
        assert c.post(f"/api/vendors/{vendor['id']}/assessments", headers=second, json={"security":3,"privacy":3,"resilience":3}).status_code == 404
        assert c.post("/api/vendors", headers=first, json={"name":"Bad","service":"X","owner_email":"invalid","data_access":"all","criticality":"urgent","next_review":"bad"}).status_code == 422


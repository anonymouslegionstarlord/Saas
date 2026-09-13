from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app


def auth(client, email, organization="Example Org"):
    response = client.post("/api/auth/register", json={"organization": organization, "email": email, "password": "strong-pass-123"})
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def grant(days=10, requested=2500000, status="submitted"):
    return {"funder": "Civic Foundation", "program": "Community Labs", "deadline": (date.today() + timedelta(days=days)).isoformat(), "requested_cents": requested, "awarded_cents": 0, "owner": "Ada Grant", "status": status, "notes": "Impact program"}


def test_grant_workflow_and_dashboard(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "test.db"))
    with TestClient(app) as client:
        headers = auth(client, "owner@example.com")
        created = client.post("/api/grants", json=grant(), headers=headers)
        assert created.status_code == 201
        item = created.json()
        payload = grant(status="awarded") | {"awarded_cents": 2000000}
        assert client.put(f"/api/grants/{item['id']}", json=payload, headers=headers).status_code == 200
        metrics = client.get("/api/dashboard", headers=headers).json()
        assert metrics == {"total": 1, "requested_cents": 2500000, "awarded_cents": 2000000, "due_soon": 0}


def test_validation_and_tenant_isolation(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", str(tmp_path / "isolated.db"))
    with TestClient(app) as client:
        first = auth(client, "first@example.com", "First")
        second = auth(client, "second@example.com", "Second")
        item = client.post("/api/grants", json=grant(), headers=first).json()
        assert client.get("/api/grants", headers=second).json() == []
        assert client.put(f"/api/grants/{item['id']}", json=grant(), headers=second).status_code == 404
        assert client.post("/api/grants", json=grant(requested=0), headers=first).status_code == 422
        assert client.post("/api/grants", json=grant(status="unknown"), headers=first).status_code == 422


import importlib

from fastapi.testclient import TestClient


def test_tenant_isolation_and_metric_flow(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("APP_SECRET", "test-secret-with-enough-entropy")
    import app.main
    importlib.reload(app.main)
    client = TestClient(app.main.app)

    first = client.post("/api/auth/register", json={"workspace":"North","name":"Nora","email":"nora@example.com","password":"password1"}).json()
    second = client.post("/api/auth/register", json={"workspace":"South","name":"Sam","email":"sam@example.com","password":"password2"}).json()
    h1 = {"Authorization": f"Bearer {first['access_token']}"}
    h2 = {"Authorization": f"Bearer {second['access_token']}"}
    metric = client.post("/api/metrics", headers=h1, json={"name":"MRR","unit":"USD","target":10000,"owner":"Nora"})
    assert metric.status_code == 201
    assert client.post(f"/api/metrics/{metric.json()['id']}/checkins", headers=h1, json={"value":4200}).status_code == 201
    assert len(client.get("/api/metrics", headers=h1).json()) == 1
    assert client.get("/api/metrics", headers=h2).json() == []
    assert client.post(f"/api/metrics/{metric.json()['id']}/checkins", headers=h2, json={"value":1}).status_code == 404


def test_validation_and_bad_login(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "validation.db"))
    import app.main
    importlib.reload(app.main)
    client = TestClient(app.main.app)
    assert client.post("/api/auth/register", json={"workspace":"X","name":"A","email":"bad","password":"short"}).status_code == 422
    assert client.post("/api/auth/login", json={"email":"none@example.com","password":"whatever"}).status_code == 401


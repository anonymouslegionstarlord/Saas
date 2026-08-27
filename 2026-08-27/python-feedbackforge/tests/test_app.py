import importlib
from fastapi.testclient import TestClient

def test_public_submission_and_tenant_isolation(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "feedback.db"))
    monkeypatch.setenv("APP_SECRET", "unit-test-secret")
    import app.main
    importlib.reload(app.main)
    client = TestClient(app.main.app)
    one = client.post("/api/auth/register", json={"workspace":"North Star","name":"Nora","email":"nora@example.com","password":"password1"}).json()
    two = client.post("/api/auth/register", json={"workspace":"South Star","name":"Sam","email":"sam@example.com","password":"password2"}).json()
    h1, h2 = {"Authorization":f"Bearer {one['access_token']}"}, {"Authorization":f"Bearer {two['access_token']}"}
    key = client.get("/api/boards", headers=h1).json()[0]["public_key"]
    item = client.post(f"/api/public/boards/{key}/feedback", json={"title":"Export CSV","details":"Please add export support","customer_email":"buyer@example.com"})
    assert item.status_code == 201
    assert len(client.get("/api/feedback", headers=h1).json()) == 1
    assert client.get("/api/feedback", headers=h2).json() == []
    assert client.patch(f"/api/feedback/{item.json()['id']}", headers=h2, json={"status":"planned","priority":"high"}).status_code == 404
    assert client.patch(f"/api/feedback/{item.json()['id']}", headers=h1, json={"status":"planned","priority":"high"}).json()["status"] == "planned"

def test_validation_and_unknown_board(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "invalid.db"))
    import app.main
    importlib.reload(app.main)
    client = TestClient(app.main.app)
    assert client.post("/api/auth/register", json={"workspace":"x","name":"x","email":"bad","password":"short"}).status_code == 422
    assert client.post("/api/public/boards/missing/feedback", json={"title":"Valid title","details":"Long enough","customer_email":"a@b.com"}).status_code == 404

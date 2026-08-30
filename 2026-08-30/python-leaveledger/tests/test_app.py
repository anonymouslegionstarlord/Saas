import importlib
from fastapi.testclient import TestClient
def test_leave_flow_and_isolation(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"leave.db"));monkeypatch.setenv("APP_SECRET","test-secret")
    import app.main
    importlib.reload(app.main);client=TestClient(app.main.app)
    one=client.post("/api/auth/register",json={"workspace":"North","name":"Nora","email":"nora@example.com","password":"password1"}).json();two=client.post("/api/auth/register",json={"workspace":"South","name":"Sam","email":"sam@example.com","password":"password2"}).json()
    h1={"Authorization":"Bearer "+one["access_token"]};h2={"Authorization":"Bearer "+two["access_token"]}
    request=client.post("/api/requests",headers=h1,json={"employee_name":"Alex","employee_email":"a@example.com","leave_type":"annual","start_date":"2030-01-01","end_date":"2030-01-03","reason":"Family holiday"}).json()
    assert request["days"]==3 and client.get("/api/requests",headers=h2).json()==[]
    assert client.patch("/api/requests/"+str(request["id"]),headers=h2,json={"status":"approved"}).status_code==404
    assert client.patch("/api/requests/"+str(request["id"]),headers=h1,json={"status":"approved"}).json()["status"]=="approved"
    assert client.get("/api/summary",headers=h1).json()["approved_days"]==3
def test_date_validation(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_PATH",str(tmp_path/"invalid.db"))
    import app.main
    importlib.reload(app.main);client=TestClient(app.main.app)
    user=client.post("/api/auth/register",json={"workspace":"Valid","name":"Owner","email":"o@example.com","password":"password1"}).json();h={"Authorization":"Bearer "+user["access_token"]}
    response=client.post("/api/requests",headers=h,json={"employee_name":"Alex","employee_email":"a@example.com","leave_type":"annual","start_date":"2030-01-03","end_date":"2030-01-01","reason":"Invalid range"})
    assert response.status_code==422

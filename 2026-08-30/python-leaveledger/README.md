# LeaveLedger

LeaveLedger is a multi-tenant leave-management SaaS MVP. Teams submit dated leave requests, calculate inclusive leave days, approve or reject pending requests, and track approved and sick-day totals.

## Features

- Workspace registration and JWT authentication with PBKDF2 password hashing
- Tenant-owned annual, sick and unpaid leave requests
- Inclusive date calculation and invalid-range protection
- Pending, approved and rejected workflow with summary totals
- Responsive dashboard, Pydantic validation and SQLite constraints
- Integration tests proving decisions and tenant isolation

## Technology stack

Python 3.11+, FastAPI, SQLite, Pydantic, PyJWT, HTML/CSS/JavaScript and pytest.

## Prerequisites and installation

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
~~~

Windows activation: .venv\Scripts\activate.

## Configuration

Set APP_SECRET, DATABASE_PATH and TOKEN_TTL_MINUTES from .env. Use a long random APP_SECRET and never commit .env.

~~~bash
set -a; source .env; set +a
~~~

## Database setup

SQLite creates tables automatically on first start. Tests generate sample tenants and leave requests in temporary databases.

## Run and test

~~~bash
uvicorn app.main:app --reload
pytest -q
~~~

Open http://127.0.0.1:8000 or /docs for Swagger.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Create workspace administrator |
| POST | /api/auth/login | Issue access token |
| GET/POST | /api/requests | List, filter or submit requests |
| PATCH | /api/requests/{id} | Approve or reject a pending request |
| GET | /api/summary | Pending and approved-day totals |
| GET | /health | Liveness check |

Private routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start the server and register a workspace.
2. Submit an employee, leave type, date range and reason.
3. Review calculated days in the request list.
4. Approve or reject it and review updated totals.

## Production notes

Add HTTPS, PostgreSQL migrations, employee invitations, role-based approvals, holiday-aware calculations, secure token storage, audit logs, backups and monitoring before production.

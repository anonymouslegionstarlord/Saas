# RenewalRadar

RenewalRadar is a multi-tenant subscription-renewal SaaS MVP. Teams track vendors, costs, billing cycles, owners and renewal dates, then see normalized annual spend and upcoming renewals.

## Features

- Workspace registration and JWT login with PBKDF2 password hashing
- Tenant-owned subscription portfolio with activate, pause and delete APIs
- Monthly, quarterly and yearly cost normalization
- Thirty-day renewal summary and chronological portfolio
- Pydantic validation, SQLite constraints and consistent errors
- Responsive dashboard and integration tests proving tenant isolation

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

Set APP_SECRET, DATABASE_PATH and TOKEN_TTL_MINUTES from .env. Replace APP_SECRET with a long random value and never commit .env.

~~~bash
set -a; source .env; set +a
~~~

## Database setup

SQLite creates its tables automatically at first start. Add subscriptions through the dashboard; the automated tests generate sample tenants and subscriptions in temporary databases.

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
| GET/POST | /api/subscriptions | List or add owned subscriptions |
| PATCH | /api/subscriptions/{id} | Pause or activate an owned subscription |
| DELETE | /api/subscriptions/{id} | Delete an owned subscription |
| GET | /api/summary | Annual spend and renewal summary |
| GET | /health | Liveness check |

Private routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start the server and register a workspace.
2. Add a vendor, category, price, billing cycle, renewal date and owner.
3. Review normalized annual spend and upcoming renewals.
4. Pause a cancelled subscription without deleting its record.

## Production notes

Add HTTPS, PostgreSQL migrations, secure token storage, reminder workers, role-based access, audit logs, backups and monitoring before production.

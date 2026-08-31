# IncidentAtlas

IncidentAtlas is a multi-tenant incident communication SaaS MVP. Teams declare incidents, publish timeline updates, move through response states and share an isolated public status feed.

## Features

- Workspace registration and JWT authentication with PBKDF2 hashing
- Minor, major and critical tenant-owned incidents
- Investigating, identified, monitoring and resolved workflow
- Timestamped updates and unique public status keys
- Responsive command dashboard, Pydantic validation and SQLite constraints
- Integration tests proving updates, public status and tenant isolation

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

Set APP_SECRET, DATABASE_PATH and TOKEN_TTL_MINUTES from .env. Use a long random secret and never commit .env.

~~~bash
set -a; source .env; set +a
~~~

## Database setup

SQLite creates tables automatically. Registration seeds a workspace with a unique public status key; tests create sample tenants and incidents in temporary databases.

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
| GET/POST | /api/incidents | List or declare incidents |
| POST | /api/incidents/{id}/updates | Add a status update |
| GET | /api/public/status/{key} | Read public incident history |
| GET | /health | Liveness check |

Private routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start the server and register a workspace.
2. Declare an incident with severity and summary.
3. Copy the public status key from the dashboard.
4. Move the incident through response states.
5. Retrieve the public feed using the status endpoint.

## Production notes

Add HTTPS, PostgreSQL migrations, role permissions, subscriber notifications, custom domains, immutable timelines, secure token storage, backups and monitoring before production.

# PolicyPulse

PolicyPulse is a multi-tenant policy acknowledgement SaaS MVP. Teams publish versioned policies, share public acknowledgement keys, track employee acceptance and archive outdated policies.

## Features

- Workspace registration and JWT login with PBKDF2 password hashing
- Versioned, tenant-owned policies with public acknowledgement links
- Validated employee acceptance with duplicate prevention
- Per-policy acknowledgement roster and counts
- Archive and reactivate controls, responsive dashboard and SQLite constraints
- Integration tests proving public flows and cross-tenant isolation

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

SQLite creates tables automatically on first start. The integration tests create sample tenants, policies and acknowledgements in temporary databases.

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
| GET/POST | /api/policies | List or publish tenant policies |
| PATCH | /api/policies/{id} | Archive or activate a policy |
| GET | /api/policies/{id}/acknowledgements | List owned acknowledgements |
| GET | /api/public/policies/{key} | Read an active public policy |
| POST | /api/public/policies/{key}/acknowledge | Record employee acceptance |
| GET | /health | Liveness check |

Private routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start the server and register a workspace.
2. Publish a title, version and policy content.
3. Share its public key and submit an acknowledgement through Swagger.
4. Refresh the dashboard and retrieve the acknowledgement roster.
5. Archive the policy when a new version replaces it.

## Production notes

Add HTTPS, PostgreSQL migrations, verified employee invitations, secure token storage, immutable audit logs, retention controls, backups and monitoring before production.

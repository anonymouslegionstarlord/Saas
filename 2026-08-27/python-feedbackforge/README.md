# FeedbackForge

FeedbackForge is a multi-tenant customer-feedback SaaS MVP. Product teams receive feedback through a public board key, triage requests by priority and status, and keep every workspace isolated.

## Features

- Workspace registration and JWT login with PBKDF2 password hashing
- Automatically provisioned public feedback board
- Validated public submissions without exposing internal tenant IDs
- Authenticated inbox, status filtering, priority and roadmap-state updates
- Tenant ownership enforced in every private query and update
- Responsive dashboard, SQLite constraints, consistent API errors
- Integration tests covering the public flow and cross-tenant denial

## Technology stack

Python 3.11+, FastAPI, Pydantic, SQLite, PyJWT, vanilla HTML/CSS/JavaScript, pytest.

## Prerequisites and installation

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
~~~

On Windows activate with .venv\Scripts\activate.

## Configuration

Export APP_SECRET, DATABASE_PATH, and TOKEN_TTL_MINUTES from your local .env. Use a long random secret outside development and never commit .env.

~~~bash
set -a; source .env; set +a
~~~

## Database setup

SQLite tables are created automatically on first start. Registration seeds a tenant, administrator, and public Product Feedback board. Delete the local database file to reset development data.

## Run and test

~~~bash
uvicorn app.main:app --reload
pytest -q
~~~

Open http://127.0.0.1:8000; interactive API documentation is at /docs.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Create tenant, admin, and initial board |
| POST | /api/auth/login | Issue an access token |
| GET | /api/boards | List the tenant boards and public keys |
| POST | /api/public/boards/{key}/feedback | Submit customer feedback |
| GET | /api/feedback?status=new | List or filter owned feedback |
| PATCH | /api/feedback/{id} | Triage owned feedback |
| GET | /health | Liveness check |

Private endpoints require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start the API and open the dashboard.
2. Register a workspace and administrator account.
3. Copy the generated public board key.
4. Submit sample feedback in Swagger using the public endpoint.
5. Refresh the inbox and move the request from New to Planned or Shipped.

## Production notes

Add HTTPS, rate limiting and CAPTCHA on public submissions, PostgreSQL migrations, secure token storage, audit logs, backups, and monitoring before production.

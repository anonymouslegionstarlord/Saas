# MetricNest

MetricNest is a runnable multi-tenant KPI tracking SaaS MVP. A company creates a private workspace, defines measurable KPIs, records daily check-ins, and sees the latest value against each target in a responsive dashboard.

## Features

- Workspace registration and email/password login
- Signed, expiring JWT access tokens and PBKDF2 password hashing
- Strict workspace ownership on every KPI and check-in query
- KPI creation, daily value upserts, latest-value dashboard, and deletion API
- Pydantic request validation, consistent HTTP errors, SQLite constraints
- Responsive no-build web interface and interactive OpenAPI docs
- Isolated integration tests proving cross-tenant access is denied

## Technology stack

Python 3.11+, FastAPI, Pydantic, SQLite, PyJWT, vanilla HTML/CSS/JavaScript, pytest.

## Prerequisites

- Python 3.11 or newer

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## Configuration

Export values from `.env` before starting (FastAPI does not load it implicitly):

```bash
set -a; source .env; set +a
```

`APP_SECRET` must be replaced with a long random string in production. `DATABASE_PATH` selects the SQLite file and `ACCESS_TOKEN_MINUTES` controls token lifetime. Never commit `.env`.

## Database setup

SQLite tables and constraints are created automatically on first start. For a clean local database, stop the app and delete `metricnest.db`. The integration test itself creates two sample tenants and KPI data in a temporary database.

## Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` for the dashboard or `/docs` for Swagger UI.

## Tests

```bash
pytest -q
```

## API overview

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create a user and isolated workspace |
| POST | `/api/auth/login` | Obtain a bearer token |
| GET | `/api/me` | Read the signed-in user/workspace |
| GET/POST | `/api/metrics` | List or create workspace KPIs |
| POST | `/api/metrics/{id}/checkins` | Create/update a dated check-in |
| DELETE | `/api/metrics/{id}` | Delete an owned KPI |
| GET | `/health` | Liveness check |

Protected routes require `Authorization: Bearer <token>`.

## First-time user steps

1. Start the server and open the dashboard.
2. Enter a workspace, name, email, and 8+ character password.
3. Select **New metric**, define its unit, target, and owner.
4. Add today's value from the KPI card; repeating it today updates that check-in.
5. Sign out when finished. Create a second workspace to observe tenant isolation.

## Production notes

Use HTTPS, a strong externally managed secret, a managed SQL database/migration tool, rate limiting, secure cookie-based token storage, audit logs, and backup/monitoring before production deployment.

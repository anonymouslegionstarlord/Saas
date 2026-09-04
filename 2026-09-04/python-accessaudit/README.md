# AccessAudit

AccessAudit is a runnable multi-tenant access-review SaaS for IT and compliance teams. It inventories business systems, tracks user grants, schedules reviews, and records evidence-backed retain or revoke decisions.

## Features

- Workspace registration and JWT login with PBKDF2 password hashing
- Tenant-isolated systems, user grants, and review decisions
- Risk levels, system owners, roles, review deadlines, and justifications
- Pending, overdue, and high-risk dashboard summaries
- Duplicate-grant protection and auditable decision timestamps
- Responsive no-build frontend, Pydantic validation, and structured errors

## Technology stack

Python 3.11+, FastAPI, SQLite, PyJWT, HTML/CSS/JavaScript, and pytest.

## Prerequisites

- Python 3.11 or newer

## Installation and configuration

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
set -a; source .env; set +a
```

Replace `JWT_SECRET` with a long random value. `DATABASE_PATH` selects the SQLite file.

## Database setup and sample data

Tables are created on startup. Register a workspace, add a high-risk system in the UI, then use `/docs` to add a sample administrator grant and record a review decision.

## Run and test

```bash
uvicorn app.main:app --reload
pytest -q
python -m compileall app tests
```

Open <http://127.0.0.1:8000>; interactive API documentation is at `/docs`.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/dashboard`
- `POST /api/systems`
- `POST /api/systems/{id}/grants`
- `PATCH /api/grants/{id}`

Protected routes require `Authorization: Bearer <token>`. Tenant identity is derived from the verified token for every query and mutation.

## First-time-user steps

1. Create a workspace and owner account.
2. Add systems with owners and risk classifications.
3. Import access grants through the API.
4. Review each grant, choosing retain or revoke with a justification.
5. Monitor pending and overdue counts.

## Production notes

Never commit `.env` or database files. Use HTTPS, rate limiting, audit-log retention, rotated secrets, SSO, background reminders, and PostgreSQL with migrations for production.

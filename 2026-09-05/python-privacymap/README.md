# PrivacyMap

PrivacyMap is a runnable multi-tenant data-processing inventory for privacy and compliance teams. It records why data is processed, whose data it is, retention periods, lawful bases, recipients, sensitivity, owners, and review dates.

## Features

- Workspace registration and JWT login with PBKDF2 hashing
- Tenant-isolated processing activities and data categories
- Purpose, lawful basis, subjects, retention, owner, risk, and review dates
- Sensitive-data counts and due-review dashboard
- Activity lifecycle with duplicate protection
- Responsive no-build UI, Pydantic validation, and structured errors

## Technology stack

Python 3.11+, FastAPI, SQLite, PyJWT, HTML/CSS/JavaScript, and pytest.

## Prerequisites

- Python 3.11+

## Installation and configuration

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
set -a; source .env; set +a
```

Replace `JWT_SECRET` with a long random value and set `DATABASE_PATH` if required.

## Database setup and sample data

SQLite tables are created on startup. Register a workspace, add a customer-support activity in the UI, then add email-address and support-message data categories through `/docs`.

## Run and test

```bash
uvicorn app.main:app --reload
pytest -q
python -m compileall app tests
```

Open <http://127.0.0.1:8000>. API documentation is available at `/docs`.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/dashboard`
- `POST /api/activities`
- `POST /api/activities/{id}/data-items`
- `PATCH /api/activities/{id}/status`

Protected queries use the tenant ID from the verified bearer token.

## First-time-user steps

1. Create a workspace and owner account.
2. Add processing activities and review dates.
3. Add data categories, sources, recipients, and sensitivity through `/docs`.
4. Review high-risk and overdue activities.

## Production notes

Never commit `.env` or database files. Add HTTPS, rate limiting, audit logs, SSO, encrypted backups, privacy-review workflows, and PostgreSQL migrations for production.

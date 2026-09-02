# ContractCue

ContractCue is a runnable multi-tenant contract-obligation tracker for small legal, procurement, and operations teams. It turns agreements into an actionable register of dates, owners, promises, and completion states.

## Features

- Workspace registration and JWT login with PBKDF2 password hashing
- Tenant-isolated contracts and obligations
- Counterparties, internal owners, terms, values, notes, and lifecycle states
- Assigned obligations with due dates, completion, and waiver states
- Dashboard counts for active agreements and obligations due within 14 days
- Responsive no-build frontend, Pydantic validation, and structured API errors

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

Replace `JWT_SECRET` with a long random value. `DATABASE_PATH` controls the SQLite file location.

## Database setup and sample data

Tables are created automatically at startup. Create a workspace in the UI, then add an agreement such as an annual hosting MSA. Add obligations through the API documentation to generate realistic sample data.

## Run and test

```bash
uvicorn app.main:app --reload
pytest -q
python -m compileall app tests
```

Open <http://127.0.0.1:8000>; OpenAPI documentation is available at `/docs`.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/dashboard`
- `POST /api/contracts`
- `POST /api/contracts/{id}/obligations`
- `PATCH /api/obligations/{id}?status_value=done`

Protected routes use `Authorization: Bearer <token>`. Every database lookup applies the tenant ID from the verified token.

## First-time-user steps

1. Create a workspace and owner account.
2. Add agreements with counterparties, dates, value, and owner.
3. Add dated obligations from `/docs`.
4. Complete or waive obligations and monitor the due-soon dashboard.

## Production notes

Never commit `.env` or database files. Use HTTPS, rotate secrets, add rate limiting and audit logs, and migrate to PostgreSQL with managed migrations for horizontally scaled deployment.

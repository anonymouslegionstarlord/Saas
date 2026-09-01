# VendorWatch

VendorWatch is a runnable multi-tenant vendor-risk register for small security and procurement teams. It tracks supplier criticality, data access, review dates, approval state, and scored assessments without relying on paid services.

## Features

- Workspace registration and JWT login with PBKDF2 password hashing
- Tenant-isolated vendor records and assessments
- Criticality, data-access classification, owner, review date, and approval status
- Security, privacy, and resilience scoring
- Dashboard totals and overdue-review visibility
- Responsive no-build frontend, structured errors, and Pydantic validation

## Technology stack

Python 3.11+, FastAPI, SQLite, PyJWT, HTML/CSS/JavaScript, pytest.

## Prerequisites

- Python 3.11 or newer

## Installation and configuration

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Set a long random `JWT_SECRET` in `.env`. Environment variables can be exported directly; FastAPI does not read `.env` automatically. For local use: `set -a; source .env; set +a`.

## Database setup and sample data

SQLite tables are created on startup at `DATABASE_PATH`. Registering through the UI creates the first tenant and owner. Add a vendor such as “Northstar Cloud,” select confidential data/high criticality, and submit an assessment to create useful sample data.

## Run and test

```bash
uvicorn app.main:app --reload
pytest -q
python -m compileall app tests
```

Open <http://127.0.0.1:8000>. Interactive API docs are at `/docs`.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/dashboard`
- `POST /api/vendors`
- `POST /api/vendors/{id}/assessments`
- `PATCH /api/vendors/{id}/status?status_value=approved`

Protected endpoints require `Authorization: Bearer <token>`. Every vendor query is scoped by the tenant embedded in the signed token.

## First-time-user steps

1. Create a workspace and owner account.
2. Add suppliers with service, owner, data-access level, criticality, and next review date.
3. Score security, privacy, and resilience through the API.
4. Move reviewed vendors to approved or restricted and revisit items shown as due.

## Security notes

Never commit `.env` or a production database. Use HTTPS, rotate secrets, restrict CORS at the edge, and replace SQLite with a managed relational database plus migrations for multi-instance production deployments.

# CertSentinel

CertSentinel is a runnable multi-tenant credential-renewal SaaS for IT, compliance, and people teams. It tracks staff certifications, issuers, expiry dates, renewal state, and ownership without paid integrations.

## Features

- Workspace registration and JWT login with PBKDF2 password hashing
- Tenant-isolated people and certification records
- Departments, issuers, credential references, issue and expiry dates
- Active, renewing, expired, and waived lifecycle states
- Dashboard alerts for expired and next-30-day renewals
- Responsive no-build UI, Pydantic validation, and structured errors

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

Replace `JWT_SECRET` with a long random value. Set `DATABASE_PATH` to control the SQLite file location.

## Database setup and sample data

Tables are created automatically on startup. Register a workspace, add a person in the UI, then add a sample CCNA or cloud certification through `/docs`.

## Run and test

```bash
uvicorn app.main:app --reload
pytest -q
python -m compileall app tests
```

Open <http://127.0.0.1:8000>. Interactive API documentation is at `/docs`.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/dashboard`
- `POST /api/people`
- `POST /api/people/{id}/credentials`
- `PATCH /api/credentials/{id}?status_value=renewing`

Protected routes require `Authorization: Bearer <token>`. All reads and mutations use the tenant ID from the verified token.

## First-time-user steps

1. Create a workspace and owner account.
2. Add team members and their departments.
3. Record certifications with issue and expiry dates through `/docs`.
4. Mark upcoming renewals and monitor dashboard alerts.

## Production notes

Never commit `.env` or database files. Use HTTPS, rate limiting, audit events, rotated secrets, scheduled notification workers, and PostgreSQL with migrations for production.

# FindingFlow

FindingFlow is a runnable multi-tenant audit-remediation SaaS. Internal audit, security, and quality teams can plan reviews, record findings, assign owners, track deadlines, and retain evidence of verified fixes.

## Features

- Workspace registration and JWT login with PBKDF2 hashing
- Tenant-isolated audits and findings
- Audit periods, business areas, leads, severity, ownership, and deadlines
- Remediation evidence and verification timestamps
- Critical, open, and overdue dashboard counts
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

Replace `JWT_SECRET` with a long random value. Configure `DATABASE_PATH` if needed.

## Database setup and sample data

SQLite tables are created on startup. Create a workspace and audit in the UI, then use `/docs` to add a sample finding and record its remediation.

## Run and test

```bash
uvicorn app.main:app --reload
pytest -q
python -m compileall app tests
```

Open <http://127.0.0.1:8000>. API documentation is at `/docs`.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/dashboard`
- `POST /api/audits`
- `POST /api/audits/{id}/findings`
- `PATCH /api/findings/{id}`

Protected endpoints derive tenant identity from the verified bearer token.

## First-time-user steps

1. Create a workspace and owner account.
2. Plan an audit with dates, scope, and lead.
3. Add findings through `/docs`.
4. Assign remediation owners and verify completed fixes.
5. Monitor critical and overdue work.

## Production notes

Never commit `.env` or database files. Use HTTPS, SSO, role-based verification, immutable audit history, rate limiting, rotated secrets, and PostgreSQL migrations in production.

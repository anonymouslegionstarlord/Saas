# TimeLedger

TimeLedger is a runnable multi-tenant timesheet and billable-hours approval SaaS MVP. Teams organize work by client project, submit time, approve or reject entries once, and see approved revenue and budget use.

## Features

- Workspace registration and JWT sign-in with PBKDF2 password hashing
- Client projects with hourly rate and hour budget
- Billable and non-billable time submissions
- One-time approval or rejection with review notes and timestamps
- Submitted/approved hours, approved billable value and budget utilization
- Tenant-scoped queries, Pydantic validation and structured errors
- Responsive no-build browser dashboard

## Technology stack

- Python 3.11+, FastAPI and Pydantic
- SQLite
- PyJWT and PBKDF2-HMAC-SHA256
- HTML, CSS and browser JavaScript
- Pytest and FastAPI TestClient

## Prerequisites

- Python 3.11 or newer

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## Configuration

Load `.env` before startup and replace `JWT_SECRET` with a long random value. `DATABASE_PATH` selects the SQLite file and `ACCESS_TOKEN_MINUTES` controls session lifetime. Never commit the real `.env`.

## Database setup

Tables and indexes are created automatically on startup. Delete `timeledger.db` while stopped to reset local data. Tests use isolated temporary databases.

## Run commands

```bash
set -a; source .env; set +a
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`; interactive API documentation is at `/docs`.

## Test commands

```bash
pytest
python -m compileall app tests
```

Tests cover approval totals, billable value, duplicate decisions, invalid hours and cross-tenant denial.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create a workspace owner |
| POST | `/api/auth/login` | Obtain a JWT |
| GET | `/api/dashboard` | Return projects, entries and summaries |
| POST | `/api/projects` | Create a client project |
| POST | `/api/projects/{id}/entries` | Submit time |
| PATCH | `/api/entries/{id}/review` | Approve or reject submitted time |

Protected endpoints require `Authorization: Bearer <token>`.

## First-time-user steps

1. Copy `.env.example`, set a strong secret, and install dependencies.
2. Start Uvicorn and register a workspace.
3. Add a client project, its hourly rate and hour budget.
4. Submit a billable or non-billable time entry.
5. Approve or reject it with a review note and check the updated totals.
6. Run tests before extending the product.

## Production notes

Use HTTPS, migrations, a managed database, separate submitter/approver roles, immutable audit history, rate limiting and signing-key rotation before production use.


# ExpenseGate

ExpenseGate is a runnable multi-tenant expense-submission and approval SaaS MVP. Every account belongs to an isolated workspace, and every expense query and mutation is scoped to that workspace.

## Features

- Workspace registration and JWT sign-in with PBKDF2 password hashing
- Expense capture with merchant, category, date, amount and business purpose
- One-time approve/reject workflow with review notes and timestamps
- Submitted, approved and rejected spending totals
- Responsive, dependency-free browser dashboard
- Pydantic input validation, structured errors and duplicate-email handling
- SQLite persistence suitable for local evaluation

## Technology stack

- Python 3.11+, FastAPI, Pydantic
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

Load `.env` in your shell or use your process manager. Set a long random `JWT_SECRET` outside development. `DATABASE_PATH` controls the SQLite file and `ACCESS_TOKEN_MINUTES` controls session lifetime. Never commit `.env`.

## Database setup

Tables and indexes are created automatically at startup. For a clean local database, stop the app and remove `expensegate.db`. The test suite uses isolated temporary databases.

## Run

```bash
set -a; source .env; set +a
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Interactive API documentation is at `/docs`.

## Tests

```bash
pytest
python -m compileall app tests
```

Tests cover approval metrics, repeat-review protection, invalid amounts and cross-tenant access denial.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create a workspace and owner |
| POST | `/api/auth/login` | Obtain a JWT |
| GET | `/api/dashboard` | List expenses and totals |
| POST | `/api/expenses` | Submit an expense |
| PATCH | `/api/expenses/{id}/review` | Approve or reject an expense |

Protected routes require `Authorization: Bearer <token>`.

## First-time-user steps

1. Copy `.env.example` to `.env` and replace `JWT_SECRET`.
2. Install dependencies and start Uvicorn.
3. Open the dashboard and create a workspace.
4. Submit the first expense in rupees; the API stores money as integer paise.
5. Approve or reject it, supplying a review note.
6. Confirm the totals update and run `pytest` before extending the app.

## Production notes

Serve behind HTTPS, restrict allowed hosts, use a managed relational database and migrations, add role-based approval limits, rotate signing secrets, and centralize audit logs before production use.


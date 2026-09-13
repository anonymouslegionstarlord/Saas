# GrantPilot

GrantPilot is a practical multi-tenant grant opportunity and application tracker for nonprofits and research teams.

## Features

- Organization registration and JWT login with PBKDF2 password hashing
- Tenant-isolated grant CRUD operations
- Funder, program, deadline, owner, requested/awarded amount and lifecycle tracking
- Dashboard totals and deadlines due within 30 days
- Responsive, dependency-free browser dashboard served by FastAPI
- Pydantic input validation and consistent HTTP errors

## Technology stack

Python 3.11+, FastAPI, SQLite, PyJWT, Pydantic, pytest and vanilla HTML/CSS/JavaScript.

## Prerequisites

- Python 3.11 or newer
- `venv` and `pip`

## Installation and configuration

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Set a unique `JWT_SECRET` of at least 32 random characters in `.env`. `DATABASE_URL` is the SQLite file path and defaults to `grantpilot.db`.

## Database setup and running

Tables are created automatically at startup:

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

## Tests

```bash
pytest
python -m compileall -q app tests
```

Tests use isolated temporary SQLite databases and cover workflows, dashboard math, validation and cross-tenant denial.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET|POST /api/grants`
- `PUT|DELETE /api/grants/{id}`
- `GET /api/dashboard`
- `GET /health`

Protected requests require `Authorization: Bearer <token>`.

## First-time user steps

1. Copy `.env.example`, replace the signing secret and start the server.
2. Open the dashboard and create an organization account.
3. Add an opportunity with its deadline, owner and requested amount.
4. Advance its status as the application progresses; record the award amount when successful.
5. Use the dashboard to prioritize upcoming deadlines and review funding totals.

For production, use HTTPS, a managed relational database, migrations, secret management, token rotation and rate limiting.

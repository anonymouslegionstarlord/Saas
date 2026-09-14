# DecisionLog

DecisionLog is a multi-tenant meeting decision and action-item register for teams that need durable context and accountability.

## Features

- Organization registration and JWT login with PBKDF2 password hashing
- Tenant-isolated meetings, decisions and action items
- Facilitators, rationale, accountable owners, due dates and lifecycle states
- Completion and overdue dashboard metrics
- Responsive no-build web dashboard served by FastAPI
- Pydantic validation and consistent authorization/not-found errors

## Technology stack

Python 3.11+, FastAPI, SQLite, PyJWT, Pydantic, pytest and vanilla HTML/CSS/JavaScript.

## Prerequisites and installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Set a unique `JWT_SECRET` of at least 32 random characters. `DATABASE_URL` is the SQLite path.

## Database setup and run commands

SQLite tables are created automatically:

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000`; API docs are at `/docs`.

## Test commands

```bash
pytest
python -m compileall -q app tests
```

Tests use temporary databases and cover workflows, metrics, validation and cross-tenant denial.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET|POST /api/meetings`
- `GET|POST /api/decisions`
- `PATCH /api/decisions/{id}/status`
- `GET /api/dashboard`, `GET /health`

Protected routes require `Authorization: Bearer <token>`.

## First-time user steps

1. Copy the environment example, replace the signing secret and start the server.
2. Create an organization account.
3. Record a meeting with its facilitator and notes.
4. Add decisions or actions with an owner and optional deadline.
5. Update action status through the API and monitor overdue work on the dashboard.

For production, use HTTPS, managed secrets, migrations, rate limiting, token rotation and a managed database.

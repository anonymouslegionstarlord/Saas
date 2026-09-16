# SLAClock

SLAClock is a multi-tenant support-ticket SLA monitor for small customer-success and service teams.

## Features

- Organization signup and JWT login with PBKDF2 password hashing
- Tenant-isolated ticket creation, listing, status updates and deletion
- Customer, assignee, priority, opened/due timestamps and resolution tracking
- Active, breached and resolved-within-SLA dashboard metrics
- Responsive no-build browser interface
- Pydantic date/enum validation and structured errors

## Technology stack

Python 3.11+, FastAPI, SQLite, Pydantic, PyJWT, pytest and vanilla HTML/CSS/JavaScript.

## Prerequisites and installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Replace `JWT_SECRET` with 32+ random characters. `DATABASE_URL` specifies the SQLite file.

## Database setup and running

Tables are created automatically:

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000`; API documentation is at `/docs`.

## Tests

```bash
pytest
python -m compileall -q app tests
```

Tests use isolated databases and cover SLA outcomes, validation and cross-tenant denial.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET|POST /api/tickets`, `DELETE /api/tickets/{id}`
- `PATCH /api/tickets/{id}/status`
- `GET /api/dashboard`, `GET /health`

Protected routes require `Authorization: Bearer <token>`.

## First-time user steps

1. Configure the environment and start FastAPI.
2. Create an organization account.
3. Add a support ticket with its priority, owner and SLA deadline.
4. Advance its status and mark it resolved when work completes.
5. Monitor active, breached and in-SLA resolutions on the dashboard.

For production, use HTTPS, managed secrets, migrations, rate limiting, token rotation and a managed database.

# CarbonLedger

CarbonLedger is a multi-tenant organizational emissions ledger for teams starting practical carbon accounting.

## Features

- Organization signup and JWT login with PBKDF2 password hashing
- Tenant-isolated activity records and annual reduction targets
- Energy, travel, freight, material, waste and custom categories
- Quantity × emission-factor calculation with evidence notes
- Annual totals, category breakdowns and target progress
- Responsive no-build browser dashboard and Pydantic validation

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

Open `http://localhost:8000`; interactive API documentation is at `/docs`.

## Tests

```bash
pytest
python -m compileall -q app tests
```

Tests use temporary databases and cover emission math, targets, validation and tenant isolation.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET|POST /api/activities`, `DELETE /api/activities/{id}`
- `PUT /api/target`
- `GET /api/dashboard?year=2026`, `GET /health`

Protected routes require `Authorization: Bearer <token>`.

## First-time user steps

1. Configure the environment and start FastAPI.
2. Create an organization account with an optional annual target.
3. Add source activities using an appropriate verified emission factor.
4. Keep source evidence in the notes field.
5. Review annual totals and category contributions on the dashboard.

This MVP is an activity ledger, not regulatory assurance. For production add factor provenance/versioning, HTTPS, migrations, managed secrets and audit logs.

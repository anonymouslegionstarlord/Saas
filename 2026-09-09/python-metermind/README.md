# MeterMind

MeterMind is a runnable multi-tenant utility-meter monitoring SaaS MVP. Teams record cumulative readings, see interval consumption, and receive an alert when the newest usage interval exceeds the previous one by their configured threshold.

## Features

- Workspace registration and JWT sign-in with PBKDF2 password hashing
- Electricity, water and gas meter directory with locations and alert thresholds
- Chronological cumulative readings with monotonic-value protection
- Automatic interval consumption and spike detection
- Tenant-wide meter, usage and anomaly summaries
- Responsive no-build web dashboard
- Pydantic validation, structured errors and isolated tenant queries

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

Load `.env` into the process before startup. Replace `JWT_SECRET` with a long random value. `DATABASE_PATH` selects the SQLite file and `ACCESS_TOKEN_MINUTES` controls session lifetime. Never commit the real `.env`.

## Database setup

SQLite tables and indexes are created automatically. Delete `metermind.db` while the app is stopped to reset local data. Tests create isolated temporary databases.

## Run commands

```bash
set -a; source .env; set +a
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`; interactive API docs are available at `/docs`.

## Test commands

```bash
pytest
python -m compileall app tests
```

Tests cover usage calculations, spike detection, cross-tenant denial and invalid decreasing readings.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create a workspace owner |
| POST | `/api/auth/login` | Obtain a JWT |
| GET | `/api/dashboard` | Return meters, readings and summaries |
| POST | `/api/meters` | Add a utility meter |
| POST | `/api/meters/{id}/readings` | Add the next cumulative reading |

Protected endpoints require `Authorization: Bearer <token>`.

## First-time-user steps

1. Copy `.env.example`, replace the signing secret, and install dependencies.
2. Start Uvicorn and register a workspace.
3. Add a meter, select its unit, and choose a spike threshold.
4. Enter at least three cumulative readings on increasing dates.
5. Review interval usage and any anomaly flag on the dashboard.
6. Run the tests before extending the alert logic.

## Production notes

Use HTTPS, migrations and a managed database; add role permissions, calibrated seasonal baselines, alert delivery, audit logs, rate limiting and signing-key rotation before production use.


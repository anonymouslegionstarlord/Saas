# FleetLedger

FleetLedger is a runnable multi-tenant fuel-cost and efficiency SaaS MVP for small vehicle fleets. It converts consecutive odometer and fill-up records into efficiency metrics and flags vehicles that fall below their configured target.

## Features

- Workspace registration and JWT sign-in with PBKDF2 password hashing
- Vehicle registry with fuel type and minimum efficiency target
- Fuel logs with date, odometer, litres, cost, driver and notes
- Automatic distance and km/l calculation between fill-ups
- Low-efficiency alerts and tenant-wide fuel-cost totals
- Chronological and increasing-odometer safeguards
- Responsive no-build dashboard, Pydantic validation and structured errors

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

Load `.env` before startup and replace `JWT_SECRET` with a long random value. `DATABASE_PATH` controls the SQLite database and `ACCESS_TOKEN_MINUTES` controls session lifetime. Do not commit the real `.env`.

## Database setup

Tables and indexes are created automatically at startup. Delete `fleetledger.db` while the app is stopped to reset local data. Tests use temporary isolated databases.

## Run commands

```bash
set -a; source .env; set +a
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`; API documentation is at `/docs`.

## Test commands

```bash
pytest
python -m compileall app tests
```

Tests cover efficiency and cost calculations, alert thresholds, invalid odometers and tenant isolation.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create a workspace owner |
| POST | `/api/auth/login` | Obtain a JWT |
| GET | `/api/dashboard` | Return vehicles, logs and summaries |
| POST | `/api/vehicles` | Add a fleet vehicle |
| POST | `/api/vehicles/{id}/fuel-logs` | Record a fill-up |

Protected endpoints require `Authorization: Bearer <token>`.

## First-time-user steps

1. Copy `.env.example`, set a strong signing secret, and install dependencies.
2. Start Uvicorn and register a workspace.
3. Add a vehicle and set its expected minimum km/l.
4. Record two or more fill-ups with increasing dates and odometer values.
5. Review calculated efficiency, costs and alerts.
6. Run the test suite before extending the product.

## Production notes

Use HTTPS, migrations, a managed database, role-based fleet permissions, receipt storage, audit logging, rate limiting and secret rotation before production use.


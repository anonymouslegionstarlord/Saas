# ExperimentLab

ExperimentLab is a multi-tenant product experiment registry for teams that want hypotheses, metrics and outcomes in one place.

## Features

- Organization signup and JWT login with PBKDF2 password hashing
- Tenant-isolated experiment creation, listing, deletion and result capture
- Hypotheses, primary metrics, target lift, dates and lifecycle states
- Baseline/observed results with automatic average-lift and win metrics
- Responsive no-build browser dashboard
- Pydantic validation and structured authentication/not-found errors

## Technology stack

Python 3.11+, FastAPI, SQLite, Pydantic, PyJWT, pytest and vanilla HTML/CSS/JavaScript.

## Prerequisites and installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Replace `JWT_SECRET` with 32+ random characters. `DATABASE_URL` is the SQLite file path.

## Database setup and running

Tables are created automatically at startup:

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000`; interactive API docs are at `/docs`.

## Tests

```bash
pytest
python -m compileall -q app tests
```

Tests use temporary databases and cover outcomes, lift calculations, date validation and tenant isolation.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET|POST /api/experiments`
- `PATCH /api/experiments/{id}/result`, `DELETE /api/experiments/{id}`
- `GET /api/dashboard`, `GET /health`

Protected routes require `Authorization: Bearer <token>`.

## First-time user steps

1. Configure the environment and start FastAPI.
2. Create an organization account.
3. Add an experiment with a measurable hypothesis and date range.
4. Mark the final outcome through the result endpoint with baseline and observed values.
5. Review win count and average lift on the dashboard.

For production, add HTTPS, managed secrets, migrations, rate limiting, token rotation and a managed database.

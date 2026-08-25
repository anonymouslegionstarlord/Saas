# Tenant Tasks SaaS API

A runnable multi-tenant task-management API built with FastAPI and SQLite. Every task operation is scoped by the `X-Tenant-ID` header, demonstrating the core data-isolation pattern used by SaaS products.

## Features

- Create, list, update, and delete tasks
- Tenant-scoped queries and writes
- Validated tenant identifiers, payloads, and task status
- Automatic OpenAPI documentation
- Dependency-free SQLite persistence layer
- Automated tenant-isolation tests

## First-time setup

```bash
git clone https://github.com/anonymouslegionstarlord/Saas.git
cd Saas
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open the interactive API documentation at <http://127.0.0.1:8000/docs>.

## Example

```bash
curl -X POST http://127.0.0.1:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo-company" \
  -d '{"title":"Invite the team","description":"Add the first workspace members"}'

curl http://127.0.0.1:8000/api/tasks -H "X-Tenant-ID: demo-company"
```

## Test

```bash
pytest
python -m compileall -q app tests
```

## Production notes

The tenant header is a learning-friendly tenancy mechanism, not authentication. Before production use, connect the tenant to an authenticated membership, use PostgreSQL, add migrations, rate limiting, audit logs, observability, and automated backups. Never trust a tenant ID supplied by an unauthenticated public client.

Future daily SaaS projects can live in dated subdirectories without affecting this root starter.

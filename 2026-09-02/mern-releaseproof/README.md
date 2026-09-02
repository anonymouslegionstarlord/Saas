# ReleaseProof

ReleaseProof is a runnable multi-tenant release-readiness SaaS for QA and engineering teams. It combines release planning, test checks, evidence, results, and a guarded go-live decision.

## Features

- Workspace registration and JWT authentication with bcrypt hashing
- Tenant-isolated releases and test checks in MongoDB
- Functional, regression, security, performance, and deployment checks
- Priorities, execution results, evidence, and calculated readiness percentage
- Approval endpoint that blocks releases until every check passes
- Responsive React dashboard, Zod validation, centralized errors, and local seed data

## Technology stack

MongoDB, Express 5, React 19, Node.js 20+, Mongoose, Zod, JWT, bcrypt, and Vite.

## Prerequisites

- Node.js 20+ and npm 10+
- MongoDB 7+ locally or a compatible connection string

## Installation and configuration

```bash
npm install
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Set a long random `JWT_SECRET`, confirm `MONGODB_URI`, and restrict `CLIENT_ORIGIN`. Never commit either `.env` file.

## Database setup and sample data

Start MongoDB and run:

```bash
npm run seed
```

The seed creates two checks for a sample release and local-only credentials `demo@releaseproof.local` / `DemoPass123!`. Remove this account outside development.

## Run commands

```bash
npm run dev
npm run seed
npm run build
```

The API runs on port 5000 and React on port 5173.

## Test commands

```bash
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

## API overview

- `GET /api/health`
- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/releases`, `POST /api/releases`
- `POST /api/releases/{id}/checks`
- `PATCH /api/checks/{id}`
- `PATCH /api/releases/{id}/ready`

Protected routes require `Authorization: Bearer <token>`. Tenant identity always comes from the verified token, never a request body.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register a workspace or load the seed account.
3. Create a release with its target date and owner.
4. Add test checks through the API, execute them in the dashboard, and attach evidence.
5. Request readiness only after all checks pass.

## Production notes

Use HTTPS, secure headers, rate limiting, audit history, role-based approvals, secret rotation, and a managed MongoDB deployment. Dependency folders and build output are intentionally ignored.

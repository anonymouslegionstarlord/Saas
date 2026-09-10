# SampleLane

SampleLane is a runnable multi-tenant laboratory sample workflow SaaS MVP. Laboratories register clients, track samples from receipt through review, and capture final results while every query remains scoped to the authenticated workspace.

## Features

- Workspace registration and JWT authentication with bcrypt password hashing
- Client directory with contact details
- Sample intake with reference, material, test, priority and due dates
- Received, preparing, testing, review, complete and rejected stages
- Required result summary or rejection reason for terminal stages
- Active, urgent, overdue and completed metrics
- Responsive React UI, sample seed data, Zod validation and structured errors

## Technology stack

- MongoDB and Mongoose
- Express 5 and Node.js 20+
- React 19 and Vite 7
- JWT, bcrypt and Zod
- Node's built-in test runner

## Prerequisites

- Node.js 20 or newer and npm
- MongoDB 7+ locally or an accessible MongoDB deployment

## Installation

```bash
npm install
cp server/.env.example server/.env
cp client/.env.example client/.env
```

## Configuration

Set `MONGODB_URI`, a long random `JWT_SECRET`, `CLIENT_ORIGIN`, and optional port/token lifetime values in `server/.env`. Set `VITE_API_URL` in `client/.env`. Never commit the real environment files.

## Database setup and sample data

Start MongoDB, then run:

```bash
npm run seed
```

This creates a development-only lab manager, client and sample and prints the local login. Re-running the seed replaces only the demo tenant's records.

## Run commands

```bash
npm run dev
```

Open `http://localhost:5173`; the API listens on `http://localhost:5000` by default.

## Test commands

```bash
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

Tests cover sample/date validation, terminal-stage evidence requirements, and workflow metrics.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create workspace owner |
| POST | `/api/auth/login` | Obtain a JWT |
| GET | `/api/clients` | Return tenant clients, samples and metrics |
| POST | `/api/clients` | Add a client |
| POST | `/api/clients/{id}/samples` | Register a sample |
| PATCH | `/api/samples/{id}` | Update workflow stage and result |
| GET | `/api/health` | API health check |

Protected endpoints require `Authorization: Bearer <token>` and include the authenticated tenant in every ownership lookup.

## First-time-user steps

1. Copy both environment examples and replace `JWT_SECRET`.
2. Start MongoDB, install packages, and optionally seed the demo workspace.
3. Run `npm run dev` and register a laboratory workspace.
4. Add a client and register its first sample.
5. Move the sample through testing and review, then record the result.
6. Confirm workflow totals and run tests plus the production build.

## Production notes

Use HTTPS, restrictive CORS, a managed MongoDB cluster, role-based lab permissions, immutable result history, encrypted attachments, backups, rate limiting and signing-key rotation before production use.


# OnboardKit

OnboardKit is a runnable multi-tenant client-onboarding SaaS for agencies, consultancies, and customer-success teams. It organizes contacts, owners, launch dates, implementation tasks, blockers, and completion progress.

## Features

- Workspace registration and JWT authentication with bcrypt hashing
- MongoDB data ownership scoped to the authenticated tenant
- Client contacts, internal owners, target launch dates, and lifecycle states
- Discovery, data, access, training, and launch tasks
- Task results, notes, automatic progress calculation, and cascade cleanup
- Responsive React interface, Zod validation, centralized errors, and sample seed data

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

Set a strong `JWT_SECRET`, verify `MONGODB_URI`, and restrict `CLIENT_ORIGIN`. Do not commit either environment file.

## Database setup and sample data

Start MongoDB, then run:

```bash
npm run seed
```

This creates an onboarding with kickoff and access tasks plus local-only credentials `demo@onboardkit.local` / `DemoPass123!`.

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
- `GET /api/clients`, `POST /api/clients`
- `POST /api/clients/{id}/tasks`
- `PATCH /api/tasks/{id}`
- `DELETE /api/clients/{id}`

Protected endpoints require `Authorization: Bearer <token>`. Tenant identity is taken exclusively from the verified token.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register a workspace or load the seed account.
3. Create a client with a contact, owner, and launch date.
4. Add implementation tasks using the API, then complete them from the dashboard.
5. Use progress percentages and blocked states to manage each launch.

## Production notes

Use HTTPS, secure headers, rate limiting, audit events, role-based permissions, secret rotation, transactional deletion, and a managed MongoDB deployment. Dependency directories and build output are ignored.

# SponsorStack

SponsorStack is a runnable multi-tenant event-sponsorship SaaS. Event teams plan funding targets, manage sponsor contacts and packages, and move opportunities from prospect to paid.

## Features

- Workspace registration and JWT authentication with bcrypt hashing
- Tenant-isolated events and sponsor opportunities
- Venues, event dates, funding targets, contacts, tiers, and deal amounts
- Prospect, proposal, committed, paid, and lost pipeline stages
- Pipeline, committed, and collected revenue totals
- Responsive React UI, Zod validation, centralized errors, and seed data

## Technology stack

MongoDB, Express 5, React 19, Node.js 20+, Mongoose, Zod, JWT, bcrypt, and Vite.

## Prerequisites

- Node.js 20+ and npm 10+
- MongoDB 7+ locally or a compatible URI

## Installation and configuration

```bash
npm install
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Set a strong `JWT_SECRET`, verify `MONGODB_URI`, and restrict `CLIENT_ORIGIN`.

## Database setup and sample data

Start MongoDB and run `npm run seed`. This creates an event and a gold sponsor opportunity plus local credentials `demo@sponsorstack.local` / `DemoPass123!`.

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
- `GET /api/events`, `POST /api/events`
- `POST /api/events/{id}/sponsors`
- `PATCH /api/sponsors/{id}`

Protected routes derive tenant identity exclusively from the verified bearer token.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register a workspace or load the seed account.
3. Create an event and funding target.
4. Add sponsor opportunities through the API.
5. Advance opportunities and monitor committed and paid totals.

## Production notes

Use HTTPS, secure headers, rate limiting, audit logs, role-based deal approval, secret rotation, and managed MongoDB. Environment files, dependencies, and build output are ignored.

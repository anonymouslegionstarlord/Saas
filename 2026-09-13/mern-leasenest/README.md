# LeaseNest

LeaseNest is a multi-tenant property and residential lease operations MVP for small property managers.

## Features

- Organization registration, bcrypt password hashing and JWT authentication
- Tenant-scoped properties and leases on every database query
- Unit count, resident contacts, rent, deposits, dates and lifecycle status
- Active-unit conflict prevention and protected property deletion
- Occupancy, monthly rent and 30-day expiration metrics
- Responsive React dashboard, structured validation and API errors
- Repeatable sample-data seed command

## Technology stack

MongoDB, Express 5, React 19, Node.js, Mongoose, Zod, JWT, bcrypt and Vite.

## Prerequisites

- Node.js 20+
- npm 10+
- MongoDB 7+ locally or a MongoDB connection string

## Installation

```bash
npm install
npm run install:all
cp server/.env.example server/.env
cp client/.env.example client/.env
```

## Configuration and database setup

Set `MONGODB_URI`, a unique 32+ character `JWT_SECRET`, `PORT` and `CLIENT_ORIGIN` in `server/.env`. Set `VITE_API_URL` in `client/.env`. Mongoose creates collections and indexes on first use.

Optional demo data (destructive for the configured database):

```bash
npm run seed --prefix server
```

The seed login is `owner@demo.local` / `demo-pass-123`; change or remove it outside local development.

## Run commands

```bash
npm run dev
# production API
npm start --prefix server
# client production bundle
npm run build
```

The client runs at `http://localhost:5173` and API at `http://localhost:4000` by default.

## Tests

```bash
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

Tests cover property and lease validation, money constraints, date ordering, occupancy, rent and expiration calculations.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET|POST /api/properties`, `DELETE /api/properties/:id`
- `GET|POST /api/leases`, `PATCH /api/leases/:id/status`
- `GET /api/dashboard`, `GET /api/health`

All business routes require `Authorization: Bearer <token>` and derive tenant ownership from the signed token.

## First-time user steps

1. Configure MongoDB and secrets, install dependencies and start both services.
2. Create an organization account.
3. Add each managed property and its unit count.
4. Add active leases with resident, unit, rent and term details.
5. Watch occupancy and expiring leases from the dashboard; end leases through the status API before re-leasing a unit.

For production, use HTTPS, managed secret storage, refresh-token rotation, rate limiting and database backups.

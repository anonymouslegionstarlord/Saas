# EventRoster

EventRoster is a multi-tenant event registration and door check-in MVP for community organizers and small venues.

## Features

- Organization accounts with bcrypt password hashing and JWT authentication
- Tenant-scoped events and attendee rosters on every query
- Capacity limits, registration states, ticket types and duplicate prevention
- One-time attendee check-in with attendance metrics
- Registration, remaining-capacity, fill-rate and check-in dashboards
- Responsive React interface, Zod validation and structured errors
- Repeatable local sample-data seed

## Technology stack

MongoDB, Express 5, React 19, Node.js, Mongoose, Zod, JWT, bcrypt and Vite.

## Prerequisites

Node.js 20+, npm 10+ and MongoDB 7+ (or another MongoDB connection string).

## Installation and configuration

```bash
npm install
npm run install:all
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Set `MONGODB_URI`, a unique 32+ character `JWT_SECRET`, `PORT` and `CLIENT_ORIGIN` in `server/.env`. Set `VITE_API_URL` in `client/.env`.

## Database setup

Mongoose creates collections and indexes at first use. Optional seed data is destructive for the configured database:

```bash
npm run seed --prefix server
```

Demo login: `host@demo.local` / `demo-pass-123` (local development only).

## Run and test commands

```bash
npm run dev
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

The client defaults to `http://localhost:5173` and API to `http://localhost:4000`.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET|POST /api/events`, `PATCH /api/events/:id/status`
- `GET /api/events/:id/attendees`, `POST /api/attendees`
- `PATCH /api/attendees/:id/check-in`
- `GET /api/events/:id/dashboard`, `GET /api/health`

Protected requests require `Authorization: Bearer <token>`; tenant identity comes only from that token.

## First-time user steps

1. Configure MongoDB and secrets, install dependencies and start both services.
2. Create an organization account and open an event with a capacity.
3. Select the event and register attendees with ticket types.
4. Check attendees in once they arrive.
5. Monitor fill and attendance rates from the dashboard.

For production, use HTTPS, secret management, token rotation, rate limiting, database backups and role-based authorization.

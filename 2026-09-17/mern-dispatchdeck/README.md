# DispatchDeck

DispatchDeck is a multi-tenant last-mile delivery queue and proof-of-delivery MVP for small courier operations.

## Features

- Organization signup, bcrypt password hashing and JWT authentication
- Tenant-scoped delivery records on every query
- References, recipients, contact details, addresses, drivers and time windows
- Guarded queued → out-for-delivery → delivered/failed workflow
- Duplicate-reference prevention and delivery proof/failure reasons
- Queue, transit, failure and on-time delivery metrics
- Responsive React dashboard, Zod validation and sample seed data

## Technology stack

MongoDB, Express 5, React 19, Node.js, Mongoose, Zod, JWT, bcrypt and Vite.

## Prerequisites and installation

Node.js 20+, npm 10+ and MongoDB 7+.

```bash
npm install
npm run install:all
cp server/.env.example server/.env
cp client/.env.example client/.env
```

## Configuration and database setup

Set `MONGODB_URI`, a unique 32+ character `JWT_SECRET`, `PORT` and `CLIENT_ORIGIN` in `server/.env`; set `VITE_API_URL` in `client/.env`. Mongoose creates collections at first use.

Optional seed data is destructive for the configured database:

```bash
npm run seed --prefix server
```

Local demo login: `dispatcher@demo.local` / `demo-pass-123`.

## Run and test commands

```bash
npm run dev
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

Client and API default to `http://localhost:5173` and `http://localhost:4000`.

## API overview

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET|POST /api/deliveries`, `DELETE /api/deliveries/:id`
- `POST /api/deliveries/:id/dispatch`
- `POST /api/deliveries/:id/outcome`
- `GET /api/dashboard`, `GET /api/health`

Protected requests require `Authorization: Bearer <token>` and use its tenant identity.

## First-time user steps

1. Configure MongoDB and secrets, install dependencies and start both services.
2. Create an organization account.
3. Add a delivery with recipient, driver and promised window.
4. Dispatch queued deliveries from the dashboard.
5. Record delivered proof or a failure reason through the outcome API and monitor on-time performance.

For production, add HTTPS, managed secrets, role-based access, token rotation, rate limiting, geocoding and database backups.

# ProcureFlow

ProcureFlow is a multi-tenant purchase-request and approval MVP for small operations and finance teams.

## Features

- Organization signup, bcrypt password hashing and JWT authentication
- Tenant-scoped requests on every read and mutation
- Departments, vendors, amounts, needed-by dates and business justification
- Guarded draft → submitted → approved/rejected workflow
- Reviewer notes, timestamps, pending counts and approved-spend metrics
- Responsive React dashboard, Zod validation and structured errors
- Repeatable local sample-data seed

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

Configure `MONGODB_URI`, a unique 32+ character `JWT_SECRET`, `PORT` and `CLIENT_ORIGIN` in `server/.env`; configure `VITE_API_URL` in `client/.env`. Mongoose creates collections at first use.

Optional seed data is destructive for the configured database:

```bash
npm run seed --prefix server
```

Local demo login: `buyer@demo.local` / `demo-pass-123`.

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
- `GET|POST /api/requests`, `DELETE /api/requests/:id`
- `POST /api/requests/:id/submit`, `POST /api/requests/:id/review`
- `GET /api/dashboard`, `GET /api/health`

Protected requests require `Authorization: Bearer <token>`; tenant identity is derived from that token.

## First-time user steps

1. Configure MongoDB and secrets, install dependencies and start both services.
2. Create an organization account.
3. Save a purchase request with vendor, amount, date and justification.
4. Submit the draft, then approve or reject it with a reviewer note through the API.
5. Monitor pending workload and approved spend on the dashboard.

For production, add HTTPS, managed secrets, token rotation, rate limiting, database backups and role-based reviewer authorization.

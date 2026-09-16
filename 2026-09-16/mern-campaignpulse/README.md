# CampaignPulse

CampaignPulse is a multi-tenant marketing campaign budget and performance tracker for small growth teams.

## Features

- Organization signup, bcrypt password hashing and JWT authentication
- Tenant-scoped campaigns on every database query
- Channels, owners, budgets, schedules and guarded lifecycle states
- Spend, revenue, impressions, clicks and conversion capture
- Portfolio CTR, conversion rate, spend and ROAS metrics
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

Set `MONGODB_URI`, a unique 32+ character `JWT_SECRET`, `PORT` and `CLIENT_ORIGIN` in `server/.env`; set `VITE_API_URL` in `client/.env`. Mongoose creates collections at first use.

Optional seed data is destructive for the configured database:

```bash
npm run seed --prefix server
```

Local demo login: `marketer@demo.local` / `demo-pass-123`.

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
- `GET|POST /api/campaigns`, `DELETE /api/campaigns/:id`
- `PATCH /api/campaigns/:id/status`
- `PATCH /api/campaigns/:id/performance`
- `GET /api/dashboard`, `GET /api/health`

Protected requests require `Authorization: Bearer <token>` and use its tenant identity.

## First-time user steps

1. Configure MongoDB and secrets, install dependencies and start both services.
2. Create an organization account.
3. Launch a campaign with its channel, budget, owner and date range.
4. Send performance totals to the performance endpoint as results arrive.
5. Monitor aggregate CTR, conversion rate, spend and ROAS.

For production, add HTTPS, managed secrets, token rotation, rate limiting, database backups and role-based authorization.

# ReferralDesk

ReferralDesk is a runnable multi-tenant referral-program SaaS for sales and customer-success teams. It manages advocates, unique codes, referred leads, pipeline status, deal value, and reward fulfillment.

## Features

- Workspace registration and JWT authentication with bcrypt hashing
- Tenant-isolated advocates and referrals in MongoDB
- Unique referral codes, configurable rewards, lead stages, and values
- Converted-referral enforcement before reward approval
- Pipeline, conversion, and outstanding-reward metrics
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

Start MongoDB and run `npm run seed`. The seed adds one advocate and referral plus local-only credentials `demo@referraldesk.local` / `DemoPass123!`.

## Run commands

```bash
npm run dev
npm run seed
npm run build
```

The API uses port 5000 and React uses port 5173.

## Test commands

```bash
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

## API overview

- `GET /api/health`
- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/dashboard`
- `POST /api/advocates`
- `POST /api/referrals`
- `PATCH /api/referrals/{id}`

Protected endpoints derive tenant identity exclusively from the verified bearer token.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register a workspace or load the seed account.
3. Add an advocate and reward amount.
4. Create referred leads through the API.
5. Qualify and convert referrals, then mark eligible rewards paid.

## Production notes

Use HTTPS, secure headers, rate limiting, audit logs, role-based payout approval, secret rotation, idempotent payments, and managed MongoDB. Environment files, dependencies, and build output are ignored.

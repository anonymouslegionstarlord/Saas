# WarrantyHub

WarrantyHub is a runnable multi-tenant warranty and service-claim SaaS for retailers and repair teams. It connects customers, products, serial numbers, coverage dates, issues, priorities, and resolutions.

## Features

- Workspace registration and JWT authentication with bcrypt hashing
- MongoDB warranties and claims scoped to the authenticated tenant
- Customer, product, serial-number, purchase, and expiration records
- Coverage validation that blocks claims for expired or void warranties
- Claim priority, lifecycle, resolution notes, and responsive dashboard
- Zod validation, centralized API errors, duplicate protection, and seed data

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

Set a strong `JWT_SECRET`, verify `MONGODB_URI`, and restrict `CLIENT_ORIGIN`. Never commit environment files.

## Database setup and sample data

Start MongoDB and run `npm run seed`. This creates a covered product with a sample claim and local credentials `demo@warrantyhub.local` / `DemoPass123!`.

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
- `GET /api/warranties`, `POST /api/warranties`
- `POST /api/warranties/{id}/claims`
- `PATCH /api/claims/{id}`

Protected endpoints require `Authorization: Bearer <token>`. Tenant identity always comes from the verified token.

## First-time-user steps

1. Start MongoDB and the development servers.
2. Register a workspace or load the seed account.
3. Register a product warranty with its customer and coverage dates.
4. Submit covered service claims through the API.
5. Move claims through approval, repair, and resolution states.

## Production notes

Use HTTPS, secure headers, rate limiting, audit events, role-based claim approval, secret rotation, object storage for evidence, and managed MongoDB. Dependencies and build output are ignored.

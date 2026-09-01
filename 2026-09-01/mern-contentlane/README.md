# ContentLane

ContentLane is a practical multi-tenant editorial workflow SaaS. Marketing teams create briefs, assign owners and due dates, and move content through a guarded idea-to-published lifecycle.

## Features

- Workspace registration and JWT authentication with bcrypt password hashing
- MongoDB records scoped to the authenticated tenant
- Blog, email, social, and video briefs with owners and due dates
- Enforced idea → draft → review → approved → published workflow
- Review-to-draft revision path, duplicate-title protection, filtering API, and dashboard counts
- Responsive React UI, Zod validation, centralized API errors, and seed data

## Technology stack

MongoDB, Express 5, React 19, Node.js 20+, Mongoose, Zod, JWT, bcrypt, and Vite.

## Prerequisites

- Node.js 20 or newer and npm 10+
- MongoDB 7+ locally or a Mongo-compatible connection string

## Installation and configuration

```bash
npm install
cp server/.env.example server/.env
cp client/.env.example client/.env
```

Set a long random `JWT_SECRET`, confirm `MONGODB_URI`, and keep both `.env` files uncommitted. `CLIENT_ORIGIN` controls browser CORS access.

## Database setup and sample data

Start MongoDB, then run:

```bash
npm run seed
```

This creates local demo data and the development-only login `demo@contentlane.local` / `DemoPass123!`. Change or remove it outside local development. Mongoose creates collections and indexes on first use.

## Run commands

```bash
npm run dev          # API :5000 and React :5173
npm run build        # production client build
npm run seed
```

## Test commands

```bash
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

## API overview

- `GET /api/health`
- `POST /api/auth/register`, `POST /api/auth/login`
- `GET /api/items?status=review`
- `POST /api/items`
- `PATCH /api/items/{id}/transition`
- `DELETE /api/items/{id}`

Protected routes require `Authorization: Bearer <token>`. The server derives `tenantId` from the verified JWT and never accepts it from request bodies.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Create a workspace or seed the local demonstration account.
3. Add a content brief with channel, owner, due date, and creative direction.
4. Advance work one stage at a time; send review items back to draft through the API when revisions are required.
5. Use stage totals to spot editorial bottlenecks.

## Production notes

Use HTTPS, a managed MongoDB deployment, unique rotated secrets, rate limiting, secure headers, audit logs, and a restricted CORS origin. Build output and dependency directories are intentionally ignored.

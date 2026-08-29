# AssetNest

AssetNest is a multi-tenant MERN equipment inventory SaaS MVP. Teams register assets, track availability, check equipment out to people, record returns and retain an ownership-scoped event history.

## Features

- Workspace registration, bcrypt password hashing and expiring JWT login
- Tenant-owned inventory with unique asset tags
- Available, checked-out, maintenance and retired states
- Checkout assignee and due-date validation plus return workflow
- Per-asset audit events and tenant-filtered status views
- Responsive React inventory dashboard and summary counts
- Sample seed, centralized errors, CORS allowlist and automated validation tests

## Technology stack

MongoDB, Express 5, React 19, Node.js, Mongoose, Vite, JWT and bcryptjs.

## Prerequisites

- Node.js 20.19+ and npm
- MongoDB 7+ locally or a compatible MongoDB URI

## Installation and configuration

~~~bash
npm install
npm run install:all
cp server/.env.example server/.env
cp client/.env.example client/.env
~~~

Set MONGODB_URI, JWT_SECRET, PORT, CLIENT_ORIGIN and VITE_API_URL. Replace JWT_SECRET with a long random value and never commit .env.

## Database setup and sample data

Start MongoDB, then optionally create a local demo workspace and two assets:

~~~bash
npm run seed --prefix server
~~~

Demo login: demo@assetnest.local / DemoPass123! for local use only. Mongoose creates collections and indexes automatically.

## Run, test and build

~~~bash
npm run dev
npm test
npm run build
~~~

The UI runs at http://localhost:5173 and API at http://localhost:4000.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Create workspace administrator |
| POST | /api/auth/login | Issue bearer token |
| GET/POST | /api/assets | List or create owned assets |
| POST | /api/assets/:id/checkout | Assign an available asset |
| POST | /api/assets/:id/return | Return a checked-out asset |
| PATCH | /api/assets/:id/status | Set maintenance, retired or available |
| GET | /api/assets/:id/events | Read owned asset audit history |
| GET | /api/health | Liveness check |

Asset routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register an owner and workspace.
3. Add an asset tag, name, category, serial and cost.
4. Use the checkout API to assign it with a due date.
5. Return it from the dashboard and inspect its event history.

## Production checklist

Add HTTPS, managed MongoDB, secure token storage, role permissions, barcode scanning, reminder notifications, immutable audits, backups and monitoring before production.

# ServiceGrid

ServiceGrid is a runnable multi-tenant preventive-maintenance SaaS MVP for facilities teams. It groups work orders by site, highlights overdue maintenance, and keeps all records isolated by workspace.

## Features

- Workspace registration and JWT authentication with bcrypt password hashing
- Site directory with address and responsible manager
- Preventive work orders for assets, tasks, frequency, due date, priority and assignee
- Scheduled, in-progress, completed and cancelled lifecycle
- Mandatory completion evidence and automatic completion timestamps
- Live maintenance metrics, including overdue work
- Responsive React dashboard, seed data, Zod validation and structured API errors

## Technology stack

- MongoDB and Mongoose
- Express 5 and Node.js 20+
- React 19 and Vite 7
- JWT, bcrypt and Zod
- Node's built-in test runner

## Prerequisites

- Node.js 20 or newer and npm
- MongoDB 7+ locally or an accessible MongoDB deployment

## Installation

```bash
npm install
cp server/.env.example server/.env
cp client/.env.example client/.env
```

## Configuration

Set `MONGODB_URI`, a long random `JWT_SECRET`, `CLIENT_ORIGIN`, and optional port/token lifetime values in `server/.env`. Set `VITE_API_URL` in `client/.env`. Keep both real `.env` files out of version control.

## Database setup and sample data

Start MongoDB, then run:

```bash
npm run seed
```

This creates local demo data and prints the development-only login. Re-running the seed safely replaces only that demo tenant's sites and work orders.

## Run

```bash
npm run dev
```

Open `http://localhost:5173`. The API listens on `http://localhost:5000` by default.

## Tests and build

```bash
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

Tests cover registration, work-order validation, mandatory completion notes, and maintenance/overdue metrics.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create workspace owner |
| POST | `/api/auth/login` | Obtain a JWT |
| GET | `/api/sites` | Return tenant sites, orders and metrics |
| POST | `/api/sites` | Create a site |
| POST | `/api/sites/{id}/orders` | Schedule a work order |
| PATCH | `/api/orders/{id}` | Move an order through its lifecycle |
| GET | `/api/health` | API health check |

All site and work-order endpoints require `Authorization: Bearer <token>` and enforce tenant ownership in their database filters.

## First-time-user steps

1. Copy both environment examples and replace `JWT_SECRET`.
2. Start MongoDB, install packages, and optionally seed the demo tenant.
3. Run `npm run dev`, then register a workspace.
4. Add a facility site and its first preventive work order.
5. Move the work order to completed and enter the completion note.
6. Verify dashboard totals, then run tests and the production build.

## Production notes

Use HTTPS, a managed MongoDB cluster, secret rotation, restrictive CORS, rate limiting, database backups, role-based permissions and centralized logs before production deployment.


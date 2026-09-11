# QueueFlow

QueueFlow is a runnable multi-tenant walk-in service queue SaaS MVP. Service desks create locations, issue readable tickets, move customers through the live queue, and monitor waiting and service metrics without exposing another workspace's records.

## Features

- Workspace registration and JWT authentication with bcrypt password hashing
- Multiple service locations with configurable ticket prefixes
- Daily human-readable queue ticket numbers
- Normal and priority queues with customer and service details
- Waiting, called, serving, completed and cancelled lifecycle
- Live queue counts, priority-waiting count and average service minutes
- Responsive React UI, seed data, Zod validation and structured API errors

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

Set `MONGODB_URI`, a long random `JWT_SECRET`, `CLIENT_ORIGIN`, and optional port/token lifetime values in `server/.env`. Set `VITE_API_URL` in `client/.env`. Never commit real environment files.

## Database setup and sample data

Start MongoDB, then run:

```bash
npm run seed
```

The seed creates a development-only manager, service location and waiting ticket and prints the local login. Re-running it replaces only the demo tenant's queue data.

## Run commands

```bash
npm run dev
```

Open `http://localhost:5173`; the API listens on `http://localhost:5000` by default.

## Test commands

```bash
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

Tests cover location/ticket input, lifecycle validation and queue/service-time metrics.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create workspace owner |
| POST | `/api/auth/login` | Obtain a JWT |
| GET | `/api/locations` | Return tenant locations, tickets and metrics |
| POST | `/api/locations` | Create a service location |
| POST | `/api/locations/{id}/tickets` | Issue the next ticket |
| PATCH | `/api/tickets/{id}` | Update ticket status and notes |
| GET | `/api/health` | API health check |

Protected endpoints require `Authorization: Bearer <token>` and every ownership lookup includes the authenticated tenant ID.

## First-time-user steps

1. Copy both environment examples and replace `JWT_SECRET`.
2. Start MongoDB, install packages, and optionally seed the demo workspace.
3. Run `npm run dev` and register a workspace.
4. Create a service location and choose its ticket prefix.
5. Issue a ticket, then move it through called, serving and completed.
6. Confirm queue totals and run tests plus the production build.

## Production notes

Use transactions or an atomic counter for high-concurrency ticket numbering. Also add HTTPS, restrictive CORS, role permissions, kiosk/display modes, notification delivery, backups, rate limiting and signing-key rotation.


# InvoicePilot

InvoicePilot is a practical MERN SaaS MVP for small teams to manage billing clients and invoices inside an isolated workspace. It includes a responsive revenue dashboard, secure authentication, line-item calculation, and invoice lifecycle states.

## Features

- Workspace registration plus email/password authentication
- bcrypt password hashing and two-hour JWT sessions
- MongoDB ownership filters on all client and invoice operations
- Client directory, invoice creation, automatic totals, and status API
- Unique invoice numbers per workspace and validated line items
- Responsive React dashboard with revenue, invoice, and client totals
- Central JSON error handling, request-size limits, CORS allowlist, environment configuration
- Zero-database unit tests for critical calculation/validation rules

## Technology stack

MongoDB, Express 5, React 19, Node.js (MERN), Mongoose, Vite, JSON Web Tokens, bcryptjs, Node's test runner.

## Prerequisites

- Node.js 20.19+ (required by Vite 7) and npm
- MongoDB 7+ locally or a MongoDB connection URI

## Installation

```bash
npm install
npm run install:all
cp server/.env.example server/.env
cp client/.env.example client/.env
```

## Configuration

Server variables: `PORT`, `MONGODB_URI`, `JWT_SECRET`, and `CLIENT_ORIGIN`. Client variable: `VITE_API_URL`. Replace `JWT_SECRET` with a long random value and never commit either `.env` file.

## Database setup

Start MongoDB locally (for example, `mongod --dbpath ./data`) or set `MONGODB_URI`. Mongoose creates collections and indexes on first use. Registration creates initial sample ownership data: one workspace and its administrator. Add clients through the dashboard; no external seed or paid service is required.

## Run commands

From the project root:

```bash
npm run dev
```

The React UI runs at `http://localhost:5173`; the API runs at `http://localhost:4000`.

## Test and build commands

```bash
npm test
npm run build
```

## API overview

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create workspace and administrator |
| POST | `/api/auth/login` | Get a bearer token |
| GET | `/api/auth/me` | Current authenticated user |
| GET/POST | `/api/clients` | List/create owned clients |
| DELETE | `/api/clients/:id` | Delete an owned client |
| GET/POST | `/api/invoices` | List/create owned invoices |
| PATCH | `/api/invoices/:id/status` | Move to draft, sent, or paid |
| GET | `/api/health` | Liveness check |

All client and invoice routes require `Authorization: Bearer <token>`.

## First-time user steps

1. Start MongoDB and both development servers.
2. Open the UI, choose **Register**, and create a workspace administrator.
3. Add a billing client on the left.
4. Select that client, enter an invoice number, due date, description, quantity, and rate.
5. Create the invoice and review outstanding revenue on the dashboard.

## Production checklist

Use HTTPS, a managed replica-set deployment, a strong secret manager, rate limiting, refresh-token rotation or secure cookies, audit logs, backups, monitoring, and a background worker for email/PDF delivery before production use.

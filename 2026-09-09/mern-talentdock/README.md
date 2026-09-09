# TalentDock

TalentDock is a runnable multi-tenant applicant-tracking SaaS MVP. Recruiting teams can create openings, add candidates, move them through a guarded pipeline, and view hiring totals without exposing another workspace's data.

## Features

- Workspace registration and JWT authentication with bcrypt password hashing
- Job openings with department, location and employment type
- Candidate profiles with contact details and acquisition source
- Applied, screening, interview, offer, hired and rejected pipeline stages
- Mandatory notes for hiring and rejection decisions
- Per-opening and workspace hiring metrics
- Responsive React interface, sample seed, Zod validation and structured errors

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

Set `MONGODB_URI`, a long random `JWT_SECRET`, `CLIENT_ORIGIN`, and optional port/token lifetime values in `server/.env`. Set `VITE_API_URL` in `client/.env`. Never commit either real `.env` file.

## Database setup and sample data

Start MongoDB, then run:

```bash
npm run seed
```

The command creates a local demo recruiter, one opening and one candidate, and prints the development-only login. Re-running it replaces only the demo tenant's hiring data.

## Run

```bash
npm run dev
```

Open `http://localhost:5173`; the API listens on `http://localhost:5000` by default.

## Tests and build

```bash
npm test
find server/src -name '*.js' -exec node --check {} \;
npm run build
```

Tests cover job and candidate validation, required decision notes, registration input and pipeline totals.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create workspace owner |
| POST | `/api/auth/login` | Obtain a JWT |
| GET | `/api/jobs` | Return tenant jobs, candidates and metrics |
| POST | `/api/jobs` | Create an opening |
| POST | `/api/jobs/{id}/candidates` | Add a candidate to an open job |
| PATCH | `/api/candidates/{id}` | Change stage and record notes |
| GET | `/api/health` | API health check |

Protected routes require `Authorization: Bearer <token>`. Job and candidate queries always include the authenticated tenant ID.

## First-time-user steps

1. Copy both environment examples and replace `JWT_SECRET`.
2. Start MongoDB, install packages, and optionally seed the demo tenant.
3. Run `npm run dev` and register a workspace.
4. Create an open role and add a candidate.
5. Move the candidate through interview and offer; supply notes on final decisions.
6. Confirm pipeline totals and run tests plus the production build.

## Production notes

Before production, use HTTPS, restrictive CORS, a managed MongoDB cluster, rate limiting, role-based hiring permissions, audit history, encrypted document storage, backups and signing-key rotation.


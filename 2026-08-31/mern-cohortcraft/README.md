# CohortCraft

CohortCraft is a multi-tenant MERN cohort-management SaaS MVP. Training teams create dated learning cohorts, control capacity and lifecycle, enroll learners and track individual completion progress.

## Features

- Workspace registration, bcrypt password hashing and expiring JWT login
- Tenant-owned cohorts with topics, instructors, dates and capacity
- Draft, open, active and completed cohort workflow
- Unique learner enrollment, capacity protection and progress tracking
- Tenant-filtered enrollment views and responsive React program studio
- Sample seed, centralized errors, CORS allowlist and automated tests

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

Start MongoDB, then optionally seed a local academy and FastAPI cohort:

~~~bash
npm run seed --prefix server
~~~

Demo login: demo@cohortcraft.local / DemoPass123! for local use only. Mongoose creates collections and indexes automatically.

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
| GET/POST | /api/cohorts | List or create owned cohorts |
| PATCH | /api/cohorts/:id/status | Update cohort lifecycle |
| GET/POST | /api/enrollments | List or enroll learners |
| PATCH | /api/enrollments/:id/progress | Update completion percentage |
| GET | /api/health | Liveness check |

Cohort and enrollment routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register an academy workspace.
3. Create a cohort with dates, instructor and capacity.
4. Enroll learners through the API.
5. Update progress to 100 percent to mark completion.

## Production checklist

Add HTTPS, managed MongoDB, secure token storage, instructor roles, invitations, attendance, certificates, notifications, audit logs, backups and monitoring before production.

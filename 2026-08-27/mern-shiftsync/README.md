# ShiftSync

ShiftSync is a practical multi-tenant MERN scheduling SaaS MVP for small service teams. Managers can create a private workspace, schedule employee shifts, view a chronological roster, edit schedules through the API, and remove cancelled shifts.

## Features

- Workspace registration and email/password login
- bcrypt password hashing and expiring JWT authentication
- Tenant-scoped shift listing, creation, editing, and deletion
- Validation for dates, 24-hour times, employee email, roles, and end-after-start
- Duplicate-shift protection using a workspace-aware MongoDB index
- Responsive React schedule and shift-creation interface
- Central JSON errors, CORS allowlist, request-size limit, environment configuration
- Optional local demo seed and automated validation tests

## Technology stack

MongoDB, Express 5, React 19, Node.js, Mongoose, Vite, JWT, bcryptjs.

## Prerequisites

- Node.js 20.19+ and npm
- MongoDB 7+ locally or a compatible connection URI

## Installation and configuration

~~~bash
npm install
npm run install:all
cp server/.env.example server/.env
cp client/.env.example client/.env
~~~

Set MONGODB_URI, JWT_SECRET, PORT, CLIENT_ORIGIN, and VITE_API_URL. Replace JWT_SECRET with a long random value and never commit either .env file.

## Database setup and sample data

Start MongoDB locally, then optionally create a demo workspace and two current-day shifts:

~~~bash
npm run seed --prefix server
~~~

Demo login: demo@shiftsync.local / DemoPass123! (local seed only; change or remove in any shared environment). Mongoose creates collections and indexes automatically.

## Run, test, and build

~~~bash
npm run dev
npm test
npm run build
~~~

The UI runs at http://localhost:5173 and the API at http://localhost:4000.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Create workspace administrator |
| POST | /api/auth/login | Issue bearer token |
| GET | /api/auth/me | Read signed-in user |
| GET | /api/shifts?from=&to= | List and date-filter owned shifts |
| POST | /api/shifts | Schedule a shift |
| PATCH | /api/shifts/:id | Edit an owned shift |
| DELETE | /api/shifts/:id | Remove an owned shift |
| GET | /api/health | Liveness check |

Shift routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register a manager and workspace.
3. Enter employee, date, start/end time, and role.
4. Schedule the shift and confirm it appears chronologically.
5. Use the documented PATCH or DELETE routes for schedule changes.

## Production checklist

Add HTTPS, managed MongoDB, secret management, rate limiting, secure cookie or refresh-token rotation, role-based permissions, notifications, audit trails, backups, and monitoring before production.

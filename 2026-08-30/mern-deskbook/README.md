# DeskBook

DeskBook is a multi-tenant MERN hot-desk booking SaaS MVP. Teams create office desks, reserve a desk for a date, prevent booking conflicts and manage a tenant-isolated reservation calendar.

## Features

- Workspace registration, bcrypt password hashing and expiring JWT login
- Tenant-owned desks with unique codes, locations, floors and amenities
- Date-based desk reservations with duplicate-booking protection
- Employee identity validation and cancellation workflow
- Active-desk controls and tenant-filtered booking views
- Responsive React workspace planner, sample seed and automated tests

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

Start MongoDB, then optionally seed a local workspace and two Delhi desks:

~~~bash
npm run seed --prefix server
~~~

Demo login: demo@deskbook.local / DemoPass123! for local use only. Mongoose creates collections and indexes automatically.

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
| GET/POST | /api/desks | List or create owned desks |
| PATCH | /api/desks/:id | Activate or deactivate an owned desk |
| GET/POST | /api/bookings | List, filter or create reservations |
| DELETE | /api/bookings/:id | Cancel an owned reservation |
| GET | /api/health | Liveness check |

Desk and booking routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register an owner and workspace.
3. Add a desk code, office location and floor.
4. Select the desk, date and employee to create a reservation.
5. Cancel the reservation from the planner when plans change.

## Production checklist

Add HTTPS, managed MongoDB, secure token storage, team roles, timezone-aware policies, check-in expiry, QR codes, audit logs, backups and monitoring before production.

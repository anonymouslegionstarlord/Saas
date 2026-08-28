# FormFlow

FormFlow is a multi-tenant MERN form-builder SaaS MVP. Teams create published forms with typed fields, share public keys, accept validated responses, and review response totals and data inside their workspace.

## Features

- Workspace registration, bcrypt password hashing and expiring JWT login
- Form builder supporting text, textarea, email and number fields
- Unique public form links with publish and unpublish control
- Public response validation based on each form schema
- Tenant-filtered form management, response counts and response listing
- Responsive React form studio, centralized API errors and CORS allowlist
- Sample seed and automated field/answer validation tests

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

Start MongoDB, then optionally create a local demo workspace and product survey:

~~~bash
npm run seed --prefix server
~~~

Demo login: demo@formflow.local / DemoPass123! for local use only. Mongoose creates collections and indexes automatically.

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
| GET/POST | /api/forms | List or create tenant forms |
| PATCH | /api/forms/:id/published | Publish or unpublish |
| GET | /api/forms/:id/responses | List owned responses |
| GET | /api/public/forms/:key | Read a published form |
| POST | /api/public/forms/:key/responses | Submit validated answers |
| GET | /api/health | Liveness check |

Private routes require Authorization: Bearer TOKEN.

## First-time-user steps

1. Start MongoDB and both development servers.
2. Register an owner and workspace.
3. Create a form title, description and first required question.
4. Copy its public key and retrieve it through the public endpoint.
5. Submit answers, then refresh the studio to see the response count.

## Production checklist

Add HTTPS, managed MongoDB, secure token storage, rate limiting and CAPTCHA for public submissions, spam controls, audit trails, backups and monitoring before production.

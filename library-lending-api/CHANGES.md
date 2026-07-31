# Library Lending API — Delivery Summary

## 1. Problem statement

The starting application was a basic FastAPI library circulation service for
patron registration, catalog management, and book lending. Although the happy
path worked, it was not ready for production: it had no authentication,
security controls, migration-based schema management, or reliable protection
against duplicate and concurrent checkout requests.

The task was to make the API production-ready, secure it with authenticated
patron access, preserve accurate inventory, test normal and error flows, and
provide repeatable local setup and sample data.

## 2. What the project does

The project provides a REST API for a small library. It lets authenticated
patrons create accounts, sign in, view library data, borrow available books,
view their own loans, and return their own books. It also supports catalog and
patron management, database migrations, sample data, and scripted scenario
testing.

## 3. Solution and issues addressed

### Authentication and authorization

- Added `POST /auth/signup` and `POST /auth/signin`.
- Passwords are salted and hashed with scrypt; plaintext passwords are never
  stored.
- Added signed, expiring JWT bearer tokens.
- Protected user, catalog, and loan endpoints, and enforced ownership rules so
  a patron can only view their own profile and loans, or borrow and return
  books for their own account.

### Data correctness and reliability

- Added Alembic migrations for the schema, idempotency constraint, inventory
  upper-bound constraint, and password-hash column.
- Added database constraints to prevent negative inventory and prevent
  available copies from exceeding total copies.
- Added idempotency support for checkout requests so client retries do not
  create duplicate loans.
- Kept database sessions scoped to each request and configured connection-pool
  health checks and recycling.

### Local setup and testability

- Added repeatable SQL seed data: two patrons, three books, and two active
  loans. It is safe to run repeatedly.
- Added and updated scenario tooling, including bearer-token support for the
  authenticated API.
- Documented a local PostgreSQL workflow using `psql`; Docker is not required.

### Verification completed

- Applied migrations to local PostgreSQL 18.
- Loaded the seed data successfully with `psql`.
- Started the API locally and verified its health endpoint.
- Ran the authenticated borrow-and-return flow successfully using `BOOK-003`.
- Verified the out-of-stock case for `BOOK-001`, which correctly returned a
  `400` response because both seeded copies are already loaned out.

## Running locally

1. Create the database: `psql -U postgres -d postgres -c "CREATE DATABASE librarydb;"`
2. Set `DATABASE_URL` in `.env` for your local credentials.
3. Run migrations: `uv run alembic upgrade head`
4. Load sample data: `psql -U postgres -d librarydb -f sql/seed_data.sql`
5. Start the API: `uv run uvicorn app.main:app --reload --port 8000`

Create an account through `/auth/signup`, then pass its bearer token to the
scenario runner with `--token`.

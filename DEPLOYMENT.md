# Library Lending API - Deployment Guide

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 16 or newer
- uv
- Git

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd library-lending-api
```

## Step 2: Set Up PostgreSQL

Install PostgreSQL locally and ensure its server is running on port 5432.
Create the development database once:

```bash
psql -U postgres -d postgres -c "CREATE DATABASE librarydb;"
```

## Step 3: Install Dependencies

```bash
uv sync
```

## Step 4: Apply Database Migrations

For a new database:

```bash
uv run alembic upgrade head
```

For a database created before migrations were introduced, verify that no
duplicate idempotency keys exist, then run:

```bash
uv run alembic stamp 20260730_01
uv run alembic upgrade head
```

## Step 5: Configure Environment (optional)

```bash
# .env (optional)
DATABASE_URL=postgresql+psycopg2://postgres:<password>@localhost:5432/librarydb
```

## Step 6: Run the Application

```bash
uv run uvicorn app.main:app --reload --port 8000
```

## Step 7: Verify

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## Step 8: Seed Data (optional)

```bash
psql -U postgres -d librarydb -f sql/seed_data.sql
```

## Testing Guide

**Register a patron**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"user_id": "PATRON-001", "email": "patron@example.com", "full_name": "Jane Reader"}'
```

**Add a book**
```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"book_id": "BOOK-001", "title": "Clean Code", "author": "Robert C. Martin", "copies_total": 2}'
```

**Check out a book**
```bash
curl -X POST http://localhost:8000/loans \
  -H "Content-Type: application/json" \
  -d '{"user_id": "PATRON-001", "book_id": "BOOK-001", "idempotency_key": "test-1"}'
```

**Return a book**
```bash
curl -X POST http://localhost:8000/loans/{loan_id}/return
```

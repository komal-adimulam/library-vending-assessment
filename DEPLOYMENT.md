# Library Lending API - Deployment Guide

## Prerequisites

- Python 3.11 or higher
- Docker (for PostgreSQL)
- uv
- Git

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd library-lending-api
```

## Step 2: Set Up PostgreSQL

```bash
docker run --name library_pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=librarydb \
  -p 5432:5432 \
  -d postgres:16
```

Verify it's running:
```bash
docker ps | grep library_pg
```

Stop / start / remove when needed:
```bash
docker stop library_pg
docker start library_pg
docker stop library_pg && docker rm library_pg   # fresh start
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
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/librarydb
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
uv run python scripts/seed_data.py --all
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

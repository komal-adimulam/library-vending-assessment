# Library Lending API - Deployment Guide

## Prerequisites

- Python 3.11 or higher
- Docker (for PostgreSQL)
- pip
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

## Step 3: Create a Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

## Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

You should see fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic,
pydantic-settings, requests in `pip list`.

## Step 5: Configure Environment (optional)

```bash
# .env (optional)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/librarydb
```

## Step 6: Run the Application

```bash
uvicorn app.main:app --reload --port 8000
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
python scripts/seed_data.py --all
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

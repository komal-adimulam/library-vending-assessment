# Library Lending API

A FastAPI-based library circulation system with patron management, catalog
management, and book checkout/return functionality.

## Quick Links

- 📖 [Complete Deployment Guide](DEPLOYMENT.md) - Step-by-step local setup instructions
- 📚 [Technical Documentation](DOCUMENTATION.md) - Architecture, flows, and development guide
- 📝 [Assessment Brief](ASSESSMENT.md) - What you're being asked to build
- 🔗 [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI (after starting server)

## Prerequisites

- Python 3.11+
- Docker
- PostgreSQL (via Docker)

## Quick Start

### 1. Start PostgreSQL

```bash
docker run --name library_pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=librarydb -p 5432:5432 -d postgres:16
```

### 2. Install Dependencies

```bash
uv sync
```

This project uses Python 3.11 (pinned in `.python-version`). `uv sync` installs
the locked dependencies into `.venv`; no manual virtual-environment activation
is needed.

### 3. Apply Database Migrations

For a new database:

```bash
uv run alembic upgrade head
```

For an existing database created before migrations were introduced, first
verify that no duplicate idempotency keys exist, then establish the legacy
baseline and apply the pending migration:

```bash
uv run alembic stamp 20260730_01
uv run alembic upgrade head
```

### 4. Run the Application

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Seed Sample Data

```bash
# Seed a catalog and a couple of patrons with loans
uv run python scripts/seed_data.py --all

# Or seed a single patron
uv run python scripts/seed_data.py PATRON-001
```

## API Endpoints

### Users (patrons)

**Register patron**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "PATRON-001",
    "email": "patron@example.com",
    "full_name": "Jane Reader",
    "phone": "+91-9876543210"
  }'
```

**Get patron**
```bash
curl http://localhost:8000/users/PATRON-001
```

**List patrons**
```bash
curl http://localhost:8000/users
```

### Books (catalog)

**Add book**
```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "BOOK-001",
    "title": "Designing Data-Intensive Applications",
    "author": "Martin Kleppmann",
    "copies_total": 2
  }'
```

**List catalog**
```bash
curl http://localhost:8000/books
```

### Loans

**Check out a book**
```bash
curl -X POST http://localhost:8000/loans \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "PATRON-001",
    "book_id": "BOOK-001",
    "idempotency_key": "checkout-123"
  }'
```

**List a patron's loans**
```bash
curl "http://localhost:8000/loans?user_id=PATRON-001"
```

**Return a book**
```bash
curl -X POST http://localhost:8000/loans/{loan_id}/return
```

## Testing Scenarios

```bash
python scripts/run_scenarios.py --scenario all
python scripts/run_scenarios.py --scenario checkout_retry
python scripts/run_scenarios.py --scenario concurrent_checkout
python scripts/run_scenarios.py --scenario concurrent_checkout --repeat 5
```

## Database Management

**Apply migrations to a new database:**
```bash
uv run alembic upgrade head
```

**Load seed data:**
```bash
docker exec -i library_pg psql -U postgres -d librarydb < sql/seed_data.sql
```

## Project Structure

```
library-lending-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration
│   ├── db.py             # Database setup
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── services.py       # Business logic
│   ├── routes_users.py   # Patron endpoints
│   ├── routes_books.py   # Catalog endpoints
│   ├── routes_loans.py   # Checkout / return endpoints
│   └── auth.py           # Authentication utilities
├── scripts/
│   ├── run_scenarios.py  # Test scenarios
│   └── seed_data.py      # Data seeding
├── sql/
│   ├── schema.sql
│   └── seed_data.sql
├── requirements.txt
├── .gitignore
├── README.md
├── DEPLOYMENT.md
├── DOCUMENTATION.md
└── ASSESSMENT.md
```

## Development

The application uses:
- FastAPI for the web framework
- SQLAlchemy 2.x for ORM
- PostgreSQL for the database
- Pydantic v2 for data validation

Database schema changes are applied with Alembic migrations before starting
the application.

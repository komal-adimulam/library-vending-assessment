# Library Lending API - Technical Documentation

## Project Overview

The Library Lending API is a FastAPI backend for a library circulation
system: registering patrons, managing a book catalog, and handling
checkout/return of books. It is presented as a production-ready system,
with layered architecture, database persistence, and RESTful design.

### Tech Stack
- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0.25
- **Validation**: Pydantic v2
- **Server**: Uvicorn
- **Python**: 3.11+

## Architecture

```
library-lending-api/
├── app/
│   ├── main.py           # Application entry point, router registration
│   ├── config.py         # Environment configuration
│   ├── db.py             # Database connection and session management
│   ├── models.py         # SQLAlchemy ORM models (User, Book, Loan)
│   ├── schemas.py        # Pydantic request/response models
│   ├── services.py       # Business logic layer
│   ├── routes_users.py   # Patron endpoints
│   ├── routes_books.py   # Catalog endpoints
│   ├── routes_loans.py   # Checkout / return endpoints
│   └── auth.py           # Authentication framework (extensible)
├── scripts/
│   ├── run_scenarios.py
│   └── seed_data.py
├── sql/
│   ├── schema.sql
│   └── seed_data.sql
```

### Layered architecture

```
API Layer (routes_*.py)
        │
Business Logic (services.py)
        │
Data Access Layer (SQLAlchemy models)
        │
PostgreSQL
```

## Database Schema

### `users`
| Column | Type | Notes |
|---|---|---|
| user_id | VARCHAR(100) PK | e.g. `PATRON-001` |
| email | VARCHAR(255) UNIQUE NOT NULL | |
| full_name | VARCHAR(255) NOT NULL | |
| phone | VARCHAR(20) NULLABLE | |
| created_at | TIMESTAMP | |
| is_active | VARCHAR(10) | |

### `books`
| Column | Type | Notes |
|---|---|---|
| book_id | VARCHAR(100) PK | e.g. `BOOK-001` |
| title | VARCHAR(255) NOT NULL | |
| author | VARCHAR(255) NOT NULL | |
| isbn | VARCHAR(20) NULLABLE | |
| copies_total | INTEGER NOT NULL | CHECK >= 0 |
| copies_available | INTEGER NOT NULL | CHECK >= 0 |
| created_at | TIMESTAMP | |

### `loans`
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR(36) PK | UUID string |
| user_id | VARCHAR(100) FK → users.user_id | |
| book_id | VARCHAR(100) FK → books.book_id | |
| idempotency_key | TEXT NULLABLE | |
| status | VARCHAR(50) | `borrowed` / `returned` |
| borrowed_at | TIMESTAMP | |
| returned_at | TIMESTAMP NULLABLE | |

Relationships: User 1—N Loans, Book 1—N Loans. CASCADE DELETE on both FKs.

## API Flows

### Checkout
```
POST /loans
  → validate request
  → services.create_loan()
      - optional idempotency lookup
      - validate copies_available > 0
      - decrement copies_available, insert loan row
      - consortium "sync window" delay
  → return { loan_id, status }
```

### Return
```
POST /loans/{loan_id}/return
  → services.return_book()
      - validate loan is still open
      - increment copies_available
      - mark loan returned
  → return loan detail
```

## Local Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full step-by-step setup.

## Testing Guide

Manual testing with curl is documented in [README.md](README.md) and
[DEPLOYMENT.md](DEPLOYMENT.md). Automated scenario scripts live in
`scripts/run_scenarios.py` and exercise checkout retries, concurrent
checkouts against limited stock, and invalid-input handling.

## Development Guidelines

- Keep business logic in `services.py`; routes should stay thin.
- All new endpoints should have request validation via Pydantic schemas.
- Any endpoint that mutates data should be safe to call more than once
  (idempotent) wherever the client might reasonably retry.

-- Library Lending API schema
-- This mirrors what SQLAlchemy creates on startup; provided for manual
-- inspection / psql usage.

CREATE TABLE IF NOT EXISTS users (
    user_id     VARCHAR(100) PRIMARY KEY,
    email       VARCHAR(255) UNIQUE NOT NULL,
    full_name   VARCHAR(255) NOT NULL,
    phone       VARCHAR(20),
    password_hash VARCHAR(255),
    created_at  TIMESTAMP DEFAULT NOW(),
    is_active   VARCHAR(10) DEFAULT 'true'
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE TABLE IF NOT EXISTS books (
    book_id          VARCHAR(100) PRIMARY KEY,
    title            VARCHAR(255) NOT NULL,
    author           VARCHAR(255) NOT NULL,
    isbn             VARCHAR(20),
    copies_total     INTEGER NOT NULL DEFAULT 1,
    copies_available INTEGER NOT NULL DEFAULT 1,
    created_at       TIMESTAMP DEFAULT NOW(),
    CONSTRAINT check_copies_available_non_negative CHECK (copies_available >= 0),
    CONSTRAINT check_copies_total_non_negative CHECK (copies_total >= 0),
    CONSTRAINT check_copies_available_not_greater_than_total CHECK (copies_available <= copies_total)
);

CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);

CREATE TABLE IF NOT EXISTS loans (
    id               VARCHAR(36) PRIMARY KEY,
    user_id          VARCHAR(100) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    book_id          VARCHAR(100) NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    idempotency_key  VARCHAR(255) UNIQUE,
    status           VARCHAR(50) NOT NULL DEFAULT 'borrowed',
    borrowed_at      TIMESTAMP DEFAULT NOW(),
    returned_at      TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_loans_user_id ON loans(user_id);
CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);

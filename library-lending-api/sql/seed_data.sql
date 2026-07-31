-- Demo catalog, patrons, and active loans for local development.
-- Safe to run repeatedly after `alembic upgrade head`.

INSERT INTO users (user_id, email, full_name, phone, is_active, created_at, password_hash)
VALUES
    ('PATRON-001', 'jane.reader@example.com', 'Jane Reader', '+91-9876543210', 'true', NOW(), 'scrypt$16384$8$1$DuFQIx6iWk4nnxVEr2kJ7g$K5X-dDvqdxW-JWm6MW8H5QD4JS77qcJLrRFLYlIPNc_Y5bAvgsH1kFRCWszMUn1_sFp8WfrzBHpFnin_JKGhrg'),
    ('PATRON-002', 'sam.bookworm@example.com', 'Sam Bookworm', '+91-9876543211', 'true', NOW(), 'scrypt$16384$8$1$DuFQIx6iWk4nnxVEr2kJ7g$K5X-dDvqdxW-JWm6MW8H5QD4JS77qcJLrRFLYlIPNc_Y5bAvgsH1kFRCWszMUn1_sFp8WfrzBHpFnin_JKGhrg')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO books (book_id, title, author, isbn, copies_total, copies_available)
VALUES
    ('BOOK-001', 'Designing Data-Intensive Applications', 'Martin Kleppmann', '9781449373320', 2, 0),
    ('BOOK-002', 'Clean Code', 'Robert C. Martin', '9780132350884', 1, 1),
    ('BOOK-003', 'The Pragmatic Programmer', 'David Thomas', '9780135957059', 3, 3)
ON CONFLICT (book_id) DO NOTHING;

INSERT INTO loans (id, user_id, book_id, idempotency_key, status)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'PATRON-001', 'BOOK-001', 'seed-loan-PATRON-001-0', 'borrowed'),
    ('00000000-0000-0000-0000-000000000002', 'PATRON-002', 'BOOK-001', 'seed-loan-PATRON-002-0', 'borrowed')
ON CONFLICT (idempotency_key) DO NOTHING;

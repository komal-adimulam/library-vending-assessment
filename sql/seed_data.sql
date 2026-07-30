-- Sample data for manual testing
INSERT INTO users (user_id, email, full_name, phone) VALUES
    ('PATRON-001', 'patron1@example.com', 'Jane Reader', '+91-9876543210'),
    ('PATRON-002', 'patron2@example.com', 'Sam Bookworm', '+91-9876543211')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO books (book_id, title, author, isbn, copies_total, copies_available) VALUES
    ('BOOK-001', 'Designing Data-Intensive Applications', 'Martin Kleppmann', '9781449373320', 2, 2),
    ('BOOK-002', 'Clean Code', 'Robert C. Martin', '9780132350884', 1, 1)
ON CONFLICT (book_id) DO NOTHING;

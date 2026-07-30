#!/usr/bin/env python3
import requests
import sys

BASE_URL = "http://localhost:8000"


def seed_user(user_id: str, email: str, full_name: str, phone: str = None):
    """Create a patron."""
    print(f"Creating patron {user_id}...")

    response = requests.post(
        f"{BASE_URL}/users",
        json={
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "phone": phone
        }
    )

    if response.status_code == 201:
        data = response.json()
        print(f"\u2713 Patron created: {data['user_id']} - {data['full_name']} ({data['email']})")
        return True
    else:
        print(f"\u2717 Failed to create patron: {response.status_code}")
        if response.status_code != 404:
            print(f"  {response.text}")
        return False


def seed_book(book_id: str, title: str, author: str, copies_total: int = 2):
    """Add a title to the catalog."""
    print(f"Adding book {book_id} ({copies_total} copies)...")

    response = requests.post(
        f"{BASE_URL}/books",
        json={
            "book_id": book_id,
            "title": title,
            "author": author,
            "copies_total": copies_total
        }
    )

    if response.status_code == 201:
        data = response.json()
        print(f"\u2713 Book added: {data['book_id']} - {data['title']}")
        return True
    else:
        print(f"\u2717 Failed to add book: {response.status_code}")
        print(f"  {response.text}")
        return False


def seed_loans(user_id: str, book_ids: list):
    """Check out sample books to a patron."""
    print(f"\nChecking out {len(book_ids)} book(s) for {user_id}...")

    for i, book_id in enumerate(book_ids):
        response = requests.post(
            f"{BASE_URL}/loans",
            json={
                "user_id": user_id,
                "book_id": book_id,
                "idempotency_key": f"seed-loan-{user_id}-{i}"
            },
            timeout=10.0
        )

        if response.status_code == 201:
            data = response.json()
            print(f"\u2713 Loan created: {data['loan_id']}")
        else:
            print(f"\u2717 Failed to create loan: {response.status_code} - {response.text}")


def seed_catalog_and_patrons():
    """Seed a small catalog and a few patrons with loans."""
    books = [
        ("BOOK-001", "Designing Data-Intensive Applications", "Martin Kleppmann", 2),
        ("BOOK-002", "Clean Code", "Robert C. Martin", 1),
        ("BOOK-003", "The Pragmatic Programmer", "David Thomas", 3),
    ]

    patrons = [
        ("PATRON-001", "jane.reader@example.com", "Jane Reader", "+91-9876543210"),
        ("PATRON-002", "sam.bookworm@example.com", "Sam Bookworm", "+91-9876543211"),
    ]

    print("=" * 60)
    print("Seeding catalog")
    print("=" * 60)
    for book_id, title, author, copies in books:
        seed_book(book_id, title, author, copies)

    print("\n" + "=" * 60)
    print("Seeding patrons")
    print("=" * 60)
    for user_id, email, full_name, phone in patrons:
        print(f"\n--- Processing {user_id} ---")
        if seed_user(user_id, email, full_name, phone):
            seed_loans(user_id, ["BOOK-001"])


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        seed_catalog_and_patrons()
    else:
        user_id = sys.argv[1] if len(sys.argv) > 1 else "PATRON-001"
        email = sys.argv[2] if len(sys.argv) > 2 else f"{user_id.lower()}@example.com"
        full_name = sys.argv[3] if len(sys.argv) > 3 else "Test Patron"

        print(f"Starting data seeding for patron: {user_id}\n")

        seed_book("BOOK-001", "Designing Data-Intensive Applications", "Martin Kleppmann", 2)
        if seed_user(user_id, email, full_name, "+91-9876543210"):
            seed_loans(user_id, ["BOOK-001"])

        print("\n\u2713 Seeding complete!")


if __name__ == "__main__":
    main()

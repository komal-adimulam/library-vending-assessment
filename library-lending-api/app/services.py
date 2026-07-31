import secrets
from app.auth import hash_password
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import User, Book, Loan
from app.schemas import UserCreate, BookCreate
from app.config import settings
from datetime import datetime
import uuid
import time


def create_user(db: Session, user_data: UserCreate, password_hash: str | None = None) -> User:
    """Register a new library patron."""
    existing_user = db.query(User).filter(User.user_id == user_data.user_id).first()
    if existing_user:
        raise ValueError(f"User with ID {user_data.user_id} already exists")

    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise ValueError(f"User with email {user_data.email} already exists")

    if not password_hash:
        # Generate a cryptographically secure random password and hash it
        password_hash = hash_password(secrets.token_urlsafe(16))

    user = User(
        user_id=user_data.user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        password_hash=password_hash,
        is_active="true"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(db: Session, user_id: str) -> User:
    """Get patron by ID."""
    return db.query(User).filter(User.user_id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 100):
    """List all patrons."""
    return db.query(User).offset(skip).limit(limit).all()


def create_book(db: Session, book_data: BookCreate) -> Book:
    """Add a new title to the catalog."""
    existing = db.query(Book).filter(Book.book_id == book_data.book_id).first()
    if existing:
        raise ValueError(f"Book with ID {book_data.book_id} already exists")

    book = Book(
        book_id=book_data.book_id,
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
        copies_total=book_data.copies_total,
        copies_available=book_data.copies_total,
    )

    db.add(book)
    db.commit()
    db.refresh(book)

    return book


def get_book(db: Session, book_id: str) -> Book:
    """Get a catalog entry by ID."""
    return db.query(Book).filter(Book.book_id == book_id).first()


def list_books(db: Session, skip: int = 0, limit: int = 100):
    """List all catalog entries."""
    return db.query(Book).offset(skip).limit(limit).all()


def create_loan(db: Session, user_id: str, book_id: str, idempotency_key: str = None) -> Loan:
    """Check out one available copy of a book to a patron."""
    if idempotency_key:
        existing = db.query(Loan).filter(
            Loan.idempotency_key == idempotency_key
        ).first()
        if existing:
            if existing.user_id != user_id or existing.book_id != book_id:
                raise ValueError("Idempotency key was already used for a different checkout")
            return existing

    user_exists = db.query(User.user_id).filter(User.user_id == user_id).first()
    if not user_exists:
        raise ValueError(f"User {user_id} not found")

    book_exists = db.query(Book.book_id).filter(Book.book_id == book_id).first()
    if not book_exists:
        raise ValueError(f"Book {book_id} not found")

    # Reserve inventory in one conditional UPDATE so competing checkouts cannot
    # both reserve the final available copy.
    reservation = db.execute(
        update(Book)
        .where(
            Book.book_id == book_id,
            Book.copies_available > 0,
        )
        .values(copies_available=Book.copies_available - 1)
    )
    if reservation.rowcount != 1:
        db.rollback()
        raise ValueError(f"No available copies of {book_id}")

    loan = Loan(
        id=str(uuid.uuid4()),
        user_id=user_id,
        book_id=book_id,
        idempotency_key=idempotency_key,
        status="borrowed",
    )

    try:
        db.add(loan)
        db.commit()
        db.refresh(loan)
    except IntegrityError:
        db.rollback()
        if idempotency_key:
            existing = db.query(Loan).filter(
                Loan.idempotency_key == idempotency_key
            ).first()
            if existing:
                if existing.user_id != user_id or existing.book_id != book_id:
                    raise ValueError("Idempotency key was already used for a different checkout")
                return existing
        raise
    except Exception:
        db.rollback()
        raise

    # This is currently a configured delay; it does not contact an external
    # catalog service.
    if settings.catalog_sync_window > 0:
        poll_interval = 0.5
        elapsed = 0.0
        while elapsed < settings.catalog_sync_window:
            time.sleep(poll_interval)
            elapsed += poll_interval

    return loan


def get_loans_by_user(db: Session, user_id: str):
    """Retrieve all loans for a patron."""
    return db.query(Loan).filter(Loan.user_id == user_id).all()


def get_loan(db: Session, loan_id: str) -> Loan | None:
    """Retrieve a loan by ID."""
    return db.query(Loan).filter(Loan.id == loan_id).first()


def return_book(db: Session, loan_id: str) -> Loan:
    """Return a checked-out book and restore catalog availability."""
    returned_at = datetime.utcnow()
    returned_loan = db.execute(
        update(Loan)
        .where(
            Loan.id == loan_id,
            Loan.status == "borrowed",
        )
        .values(status="returned", returned_at=returned_at)
        .returning(Loan.book_id)
    ).scalar_one_or_none()

    if returned_loan is None:
        db.rollback()
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise ValueError(f"Loan {loan_id} not found")
        raise ValueError(f"Loan {loan_id} was already returned")

    inventory_update = db.execute(
        update(Book)
        .where(
            Book.book_id == returned_loan,
            Book.copies_available < Book.copies_total,
        )
        .values(copies_available=Book.copies_available + 1)
    )
    if inventory_update.rowcount != 1:
        db.rollback()
        raise ValueError(f"Cannot restore availability for book {returned_loan}")

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return db.query(Loan).filter(Loan.id == loan_id).first()

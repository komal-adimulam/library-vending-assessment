from sqlalchemy import Column, String, Integer, DateTime, CheckConstraint, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(100), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(String(10), default="true")

    # Relationships
    loans = relationship("Loan", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    book_id = Column(String(100), primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20), nullable=True)
    copies_total = Column(Integer, nullable=False, default=1)
    copies_available = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    loans = relationship("Loan", back_populates="book")

    __table_args__ = (
        CheckConstraint('copies_available >= 0', name='check_copies_available_non_negative'),
        CheckConstraint('copies_total >= 0', name='check_copies_total_non_negative'),
    )


class Loan(Base):
    __tablename__ = "loans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), ForeignKey('users.user_id'), nullable=False)
    book_id = Column(String(100), ForeignKey('books.book_id'), nullable=False)
    idempotency_key = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="borrowed")
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    returned_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")

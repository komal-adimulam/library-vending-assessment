from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas import BookCreate, BookDetail
from app import services
from app.auth import get_current_user
from app.schemas import AuthenticatedUser

router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookDetail, status_code=201)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Add a new title to the catalog."""
    try:
        new_book = services.create_book(db, book)
        return new_book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{book_id}", response_model=BookDetail)
def get_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Get a catalog entry by ID."""
    book = services.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("", response_model=List[BookDetail])
def list_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """List all catalog entries."""
    return services.list_books(db, skip=skip, limit=limit)

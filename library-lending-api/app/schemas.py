from pydantic import BaseModel, Field, EmailStr, SecretStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=100, pattern=r'^[A-Z]+-\d+$')
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "PATRON-001",
                "email": "patron@example.com",
                "full_name": "Jane Reader",
                "phone": "+91-9876543210"
            }
        }


class UserResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    phone: Optional[str]
    created_at: Optional[datetime] = None
    is_active: str

    class Config:
        from_attributes = True


class UserDetail(BaseModel):
    user_id: str
    email: str
    full_name: str
    phone: Optional[str]
    created_at: Optional[datetime] = None
    is_active: str

    class Config:
        from_attributes = True


class BookCreate(BaseModel):
    book_id: str = Field(..., min_length=3, max_length=100, pattern=r'^[A-Z]+-\d+$')
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    copies_total: int = Field(..., gt=0, le=10000)

    class Config:
        json_schema_extra = {
            "example": {
                "book_id": "BOOK-001",
                "title": "Designing Data-Intensive Applications",
                "author": "Martin Kleppmann",
                "isbn": "9781449373320",
                "copies_total": 3
            }
        }


class BookDetail(BaseModel):
    book_id: str
    title: str
    author: str
    isbn: Optional[str]
    copies_total: int
    copies_available: int
    created_at: datetime

    class Config:
        from_attributes = True


class LoanCreate(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=100)
    book_id: str = Field(..., min_length=3, max_length=100)
    idempotency_key: Optional[str] = Field(None, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "PATRON-001",
                "book_id": "BOOK-001",
                "idempotency_key": "loan-abc-123"
            }
        }


class LoanResponse(BaseModel):
    loan_id: str
    status: str

    class Config:
        from_attributes = True


class LoanDetail(BaseModel):
    id: str
    user_id: str
    book_id: str
    status: str
    idempotency_key: Optional[str]
    borrowed_at: datetime
    returned_at: Optional[datetime]

    class Config:
        from_attributes = True


# NOTE: reserved for the authentication layer (not yet wired up).
class AuthenticatedUser(BaseModel):
    user_id: str
    username: str


class SignUpRequest(UserCreate):
    password: SecretStr = Field(..., min_length=12, max_length=128)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "PATRON-001",
                "email": "patron@example.com",
                "full_name": "Jane Reader",
                "phone": "+91-9876543210",
                "password": "my-secure-password-123",
            }
        }


class SignInRequest(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import services
from app.auth import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models import User
from app.schemas import SignInRequest, SignUpRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
    """Create a patron account and return a bearer token."""
    try:
        user = services.create_user(db, payload, password_hash=hash_password(payload.password.get_secret_value()))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return TokenResponse(access_token=create_access_token(user))


@router.post("/signin", response_model=TokenResponse)
def signin(payload: SignInRequest, db: Session = Depends(get_db)):
    """Authenticate without revealing whether an email address is registered."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or user.is_active != "true" or not verify_password(payload.password.get_secret_value(), user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user))

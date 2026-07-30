"""Password hashing and bearer-token authentication utilities."""

import base64
import binascii
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import User
from app.schemas import AuthenticatedUser

_PASSWORD_ALGORITHM = "scrypt"
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SALT_BYTES = 16
_bearer_scheme = HTTPBearer(auto_error=False)
_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str) -> str:
    """Return a salted scrypt password hash suitable for database storage."""
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P
    )
    return f"{_PASSWORD_ALGORITHM}${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    """Constant-time verification that treats malformed hashes as invalid."""
    if not stored_hash:
        return False
    try:
        algorithm, n, r, p, encoded_salt, encoded_digest = stored_hash.split("$")
        if algorithm != _PASSWORD_ALGORITHM:
            return False
        actual = hashlib.scrypt(
            password.encode("utf-8"), salt=_b64decode(encoded_salt),
            n=int(n), r=int(r), p=int(p), dklen=len(_b64decode(encoded_digest)),
        )
        return hmac.compare_digest(actual, _b64decode(encoded_digest))
    except (ValueError, TypeError, AttributeError):
        return False


def create_access_token(user: User) -> str:
    """Create a signed, short-lived JWT for a library patron."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.user_id,
        "username": user.email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
    }
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    encoded_header = _b64encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    message = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(settings.jwt_secret.encode("utf-8"), message, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64encode(signature)}"


def _decode_access_token(token: str) -> dict:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        header = json.loads(_b64decode(encoded_header))
        if header != {"alg": "HS256", "typ": "JWT"} or settings.jwt_algorithm != "HS256":
            raise ValueError("Unexpected JWT algorithm")
        message = f"{encoded_header}.{encoded_payload}".encode("ascii")
        expected = hmac.new(settings.jwt_secret.encode("utf-8"), message, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64decode(encoded_signature)):
            raise ValueError("Invalid signature")
        payload = json.loads(_b64decode(encoded_payload))
        if not isinstance(payload.get("sub"), str) or not isinstance(payload.get("username"), str):
            raise ValueError("Invalid claims")
        if int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("Expired token")
        return payload
    except (
        ValueError,
        TypeError,
        KeyError,
        OverflowError,
        binascii.Error,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        raise _credentials_error


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """FastAPI dependency that authenticates an active bearer-token holder."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _credentials_error
    payload = _decode_access_token(credentials.credentials)
    user = db.query(User).filter(User.user_id == payload["sub"]).first()
    if user is None or user.is_active != "true" or user.email != payload["username"]:
        raise _credentials_error
    return AuthenticatedUser(user_id=user.user_id, username=user.email)

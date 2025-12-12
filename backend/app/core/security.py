# backend/app/core/security.py
"""
Security helpers: password hashing, JWT creation and verification.

Impact:
- Other modules (auth, dependencies_auth) will import these functions.
- Uses `settings.SECRET_KEY`, `settings.ALGORITHM`, and `settings.ACCESS_TOKEN_EXPIRE_MINUTES`.
- Requires python-jose and passlib in requirements.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ACCESS_COOKIE_NAME = getattr(settings, "ACCESS_TOKEN_COOKIE_NAME", "access_token_cookie")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None, extra: Optional[Dict[str, Any]] = None) -> str:
    """
    Create JWT with 'sub' claim set to subject (user id or username).
    """
    now = datetime.utcnow()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": now + expires_delta, "iat": now, "sub": str(subject)}
    if extra:
        to_encode.update(extra)
    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a token. Raises JWTError on failure.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise

    return payload


def get_subject_from_token(token: str) -> Optional[str]:
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except JWTError:
        return None

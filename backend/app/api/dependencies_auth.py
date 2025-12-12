# backend/app/api/dependencies_auth.py
"""
Authentication dependencies for cookie-based JWT auth.
- get_token_from_cookie: extracts JWT from cookie.
- get_current_user: returns authenticated user via token validation.
Uses async CRUD helpers and security functions.
"""

from typing import Optional

from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_get_db
from app import crud, schemas
from app.core import security
from app.config import settings


async def get_token_from_cookie(request: Request) -> str:
    """
    Read JWT token from configured cookie.
    Strips optional 'Bearer ' prefix.
    Raises 401 if missing.
    """
    cookie_name = getattr(settings, "ACCESS_TOKEN_COOKIE_NAME", "access_token_cookie")
    token = request.cookies.get(cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    # Support "Bearer <token>" or raw token
    if isinstance(token, str) and token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    return token


async def _get_user_from_token(db: AsyncSession, token: str) -> Optional[schemas.UserRead]:
    """
    Internal helper: decode token, get subject, fetch user from DB.
    Returns None if invalid/missing.
    """
    try:
        payload = security.decode_token(token)
    except Exception:
        return None

    sub = payload.get("sub")
    if not sub:
        return None
    
    # Try to parse subject as user ID first
    try:
        user_id = int(sub)
        user_obj = await crud.get_user(db, user_id)
        if user_obj is None:
            return None
        return schemas.UserRead.model_validate(user_obj)
    except (ValueError, TypeError):
        # Fallback: treat sub as username
        user_obj = await crud.get_user_by_username(db, sub)
        if user_obj is None:
            return None
        return schemas.UserRead.model_validate(user_obj)


async def get_current_user(
    db: AsyncSession = Depends(async_get_db),
    token: str = Depends(get_token_from_cookie),
) -> schemas.UserRead:
    """
    Public dependency for endpoints that require an authenticated user.
    Raises 401 if token invalid or user missing.
    """
    user = await _get_user_from_token(db, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

# backend/app/api/auth.py
"""
Auth router: login, logout, me, refresh (optional).
- Will set HttpOnly cookie on login.
- Returns TokenResponse in body for convenience (keeps original schema).
Impact:
- Changes how cookies are set; must match FRONTEND usage (axios withCredentials).
- Uses crud.authenticate_user, crud.get_user, and security functions.
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_get_db
from app import crud, schemas
from app.core import security
from app.config import settings
from app.api.dependencies_auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=schemas.TokenResponse)
async def login_access_token(
    response: Response,
    credentials: schemas.UserLogin,
    db: AsyncSession = Depends(async_get_db),
):
    """
    Authenticate user and set access token cookie.
    Cookie settings:
    - httponly=True: prevents JS access (security)
    - secure: True in production (HTTPS only), False in dev
    - samesite: "none" for dev (allows cross-site), "lax"/"strict" for prod
    - domain: None for localhost, ".yourdomain.com" for production
    """
    user = await crud.user.authenticate(db, identifier=credentials.username, password=credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(subject=user.id, expires_delta=access_token_expires)

    # Determine cookie domain based on environment
    cookie_domain = None
    if settings.is_production:
        cookie_domain = ".funwine.app"  # Production domain

    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        httponly=settings.COOKIE_HTTPONLY,  # Always True
        secure=settings.COOKIE_SECURE,  # False for dev, True for prod
        samesite=settings.COOKIE_SAMESITE,  # "none" for dev, "lax" for prod
        max_age=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        path="/",
        domain=cookie_domain,
    )

    return schemas.TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
    )


@router.post("/logout")
async def logout(response: Response):
    """
    Clear the access token cookie.
    Must match the domain and path used when setting the cookie.
    """
    cookie_domain = None
    if settings.is_production:
        cookie_domain = ".funwine.app"

    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        path="/",
        domain=cookie_domain,
    )
    return JSONResponse({"detail": "Successfully logged out"}, status_code=200)


@router.get("/me", response_model=schemas.UserRead)
async def read_users_me(current_user: schemas.UserRead = Depends(get_current_user)):
    """
    Returns the current authenticated user via cookie-based auth.
    """
    return current_user

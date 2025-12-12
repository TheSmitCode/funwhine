#app/api/admin.py
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

# Fixed relative imports
from ..config import settings
from ..db.session import async_get_db
from .. import crud, schemas


# IMPORTANT:
# Your settings DO NOT define API_V1_STR.
# Use a direct, stable token URL instead.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in async_get_db():
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> schemas.UserRead:
    """
    Validate JWT and return current authenticated user.
    Returns a Pydantic UserRead model, NOT the ORM instance.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await crud.user.get(db, id=int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Convert ORM → Pydantic model (recommended)
    return schemas.UserRead.model_validate(user)


async def get_active_user(
    current_user: schemas.UserRead = Depends(get_current_user)
) -> schemas.UserRead:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# app/api/user_prefs.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import async_get_db
from ..models.user import User
from .. import schemas, crud
from ..schemas import UserRead, UserUpdate
from .dependencies_auth import get_current_user


router = APIRouter(tags=["User Preferences"])


@router.get("/me", response_model=UserRead)
async def get_me(current_user: UserRead = Depends(get_current_user)):
    """
    Return current authenticated user with UI preferences.
    """
    return current_user


@router.patch("/me/preferences", response_model=UserRead)
async def update_preferences(
    payload: UserUpdate,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Update the current user's UI preferences.
    Only the fields explicitly sent in the request body are updated.
    """
    user = await crud.get_user(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.model_dump(exclude_unset=True)

    allowed = {
        "ui_theme",
        "ui_sidebar",
        "ui_navbar",
        "ui_font_scale",
        "ui_simple_mode",
        "ui_features",
    }

    updated = False

    for key, value in data.items():
        if key in allowed:
            setattr(user, key, value)
            updated = True

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No UI preference fields provided",
        )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return schemas.UserRead.model_validate(user)

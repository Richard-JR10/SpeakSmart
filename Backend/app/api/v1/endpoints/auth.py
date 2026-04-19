from collections.abc import Mapping
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_current_user, get_db
from app.core.exceptions import NotFoundException
from app.db.models.user import User
from app.schemas.user import UserRegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    body: UserRegisterRequest,
    claims: Mapping[str, object] = Depends(get_current_claims),
    db: AsyncSession = Depends(get_db),
):
    uid = str(claims["uid"])
    result = await db.execute(select(User).where(User.uid == uid))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        return existing_user

    user = User(
        uid=uid,
        email=str(claims.get("email", "")),
        display_name=body.display_name.strip(),
        role=body.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
async def get_me(
    claims: Mapping[str, object] = Depends(get_current_claims),
    db: AsyncSession = Depends(get_db)
):
    uid = str(claims["uid"])
    result = await db.execute(select(User).where(User.uid == uid))
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise NotFoundException("PROFILE_SETUP_REQUIRED")

    current_user.last_login = datetime.now(timezone(timedelta(hours=8)))
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/verify")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    return {
        "valid": True,
        "uid": current_user.uid,
        "role": current_user.role,
    }

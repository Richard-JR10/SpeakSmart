from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
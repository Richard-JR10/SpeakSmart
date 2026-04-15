from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])

@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if body.display_name is not None:
        current_user.display_name = body.display_name
    if body.class_id is not None:
        current_user.class_id = body.class_id

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
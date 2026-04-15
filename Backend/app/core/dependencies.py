from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.user import User
from app.services.firebase_auth import verify_firebase_token
from app.core.exceptions import UnauthorizedException, ForbiddenException

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials

    try:
        claims = await verify_firebase_token(token)
    except ValueError:
        raise UnauthorizedException("Invalid or expired token")
    
    uid = claims.get("uid")
    if not uid:
        raise UnauthorizedException("Token missing 'uid' claim")
    
    result = await db.execute(select(User).where(User.uid == uid))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            uid=uid,
            email=claims.get("email",""),
            display_name=claims.get("name",claims.get("email","Unknown")),
            role="student"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user

async def require_instructor(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "instructor":
        raise ForbiddenException("Instructor access required")
    return current_user

async def require_student(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "student":
        raise ForbiddenException("Student access required")
    return current_user

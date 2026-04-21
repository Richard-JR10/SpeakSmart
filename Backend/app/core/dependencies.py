from collections.abc import Mapping

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.class_ import Class, ClassMembership
from app.db.models.user import User
from app.services.firebase_auth import verify_firebase_token
from app.core.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
)

bearer_scheme = HTTPBearer()

async def get_current_claims(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Mapping[str, object]:
    token = credentials.credentials

    try:
        claims = verify_firebase_token(token)
    except ValueError:
        raise UnauthorizedException("Invalid or expired token")

    uid = claims.get("uid")
    if not uid:
        raise UnauthorizedException("Token missing 'uid' claim")

    return claims


async def get_current_user(
    claims: Mapping[str, object] = Depends(get_current_claims),
    db: AsyncSession = Depends(get_db)
) -> User:
    uid = str(claims["uid"])

    result = await db.execute(select(User).where(User.uid == uid))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("PROFILE_SETUP_REQUIRED")

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


async def get_owned_class(
    db: AsyncSession,
    class_id: str,
    instructor_uid: str,
) -> Class:
    result = await db.execute(
        select(Class).where(
            Class.class_id == class_id,
            Class.instructor_uid == instructor_uid,
        )
    )
    class_ = result.scalar_one_or_none()
    if not class_:
        raise NotFoundException(f"Class '{class_id}' not found")
    return class_


async def get_class_membership(
    db: AsyncSession,
    class_id: str,
    user_uid: str,
) -> ClassMembership:
    result = await db.execute(
        select(ClassMembership).where(
            ClassMembership.class_id == class_id,
            ClassMembership.user_uid == user_uid,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise NotFoundException("Class membership not found")
    return membership


async def get_class_student_uids(
    db: AsyncSession,
    class_id: str,
) -> list[str]:
    result = await db.execute(
        select(ClassMembership.user_uid)
        .join(User, User.uid == ClassMembership.user_uid)
        .where(
            ClassMembership.class_id == class_id,
            User.role == "student",
        )
    )
    return [row[0] for row in result.all()]

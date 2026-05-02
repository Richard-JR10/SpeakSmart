import secrets
import string
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_class_membership,
    get_class_student_uids,
    get_current_user,
    get_db,
    get_owned_class,
    require_instructor,
    require_student,
)
from app.core.exceptions import BadRequestException, NotFoundException
from app.db.models.class_ import Class, ClassMembership
from app.db.models.exercise import Exercise, ExerciseAssignment
from app.db.models.user import User
from app.schemas.class_ import (
    ClassCreateRequest,
    ClassStudentResponse,
    ClassSummaryResponse,
    JoinClassRequest,
    JoinCodeResponse,
)

router = APIRouter(prefix="/classes", tags=["classes"])

JOIN_CODE_ALPHABET = string.ascii_uppercase + string.digits


def _generate_class_id() -> str:
    return f"class_{uuid.uuid4().hex[:12]}"


def _generate_join_code() -> str:
    return "".join(secrets.choice(JOIN_CODE_ALPHABET) for _ in range(6))


async def _create_unique_join_code(db: AsyncSession) -> str:
    while True:
        join_code = _generate_join_code()
        result = await db.execute(select(Class.class_id).where(Class.join_code == join_code))
        if result.scalar_one_or_none() is None:
            return join_code


async def _get_student_counts(
    db: AsyncSession,
    class_ids: list[str],
) -> dict[str, int]:
    if not class_ids:
        return {}

    result = await db.execute(
        select(
            ClassMembership.class_id,
            func.count(ClassMembership.user_uid),
        )
        .join(User, User.uid == ClassMembership.user_uid)
        .where(
            ClassMembership.class_id.in_(class_ids),
            User.role == "student",
        )
        .group_by(ClassMembership.class_id)
    )
    return {class_id: count for class_id, count in result.all()}


@router.get("", response_model=list[ClassSummaryResponse])
async def list_my_classes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == "instructor":
        result = await db.execute(
            select(Class)
            .where(Class.instructor_uid == current_user.uid)
            .order_by(Class.created_at.desc())
        )
        classes = result.scalars().all()
        student_counts = await _get_student_counts(db, [class_.class_id for class_ in classes])

        return [
            ClassSummaryResponse(
                class_id=class_.class_id,
                name=class_.name,
                instructor_uid=class_.instructor_uid,
                instructor_name=current_user.display_name,
                join_code=class_.join_code,
                created_at=class_.created_at,
                joined_at=None,
                student_count=student_counts.get(class_.class_id, 0),
                is_owner=True,
            )
            for class_ in classes
        ]

    result = await db.execute(
        select(ClassMembership, Class, User.display_name)
        .join(Class, Class.class_id == ClassMembership.class_id)
        .join(User, User.uid == Class.instructor_uid)
        .where(ClassMembership.user_uid == current_user.uid)
        .order_by(ClassMembership.joined_at.desc())
    )
    rows = result.all()
    student_counts = await _get_student_counts(db, [class_.class_id for _, class_, _ in rows])

    return [
        ClassSummaryResponse(
            class_id=class_.class_id,
            name=class_.name,
            instructor_uid=class_.instructor_uid,
            instructor_name=instructor_name,
            join_code=None,
            created_at=class_.created_at,
            joined_at=membership.joined_at,
            student_count=student_counts.get(class_.class_id, 0),
            is_owner=False,
        )
        for membership, class_, instructor_name in rows
    ]


@router.post("", response_model=ClassSummaryResponse, status_code=201)
async def create_class(
    body: ClassCreateRequest,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    class_ = Class(
        class_id=_generate_class_id(),
        name=body.name.strip(),
        instructor_uid=current_user.uid,
        join_code=await _create_unique_join_code(db),
    )
    db.add(class_)
    await db.commit()
    await db.refresh(class_)

    return ClassSummaryResponse(
        class_id=class_.class_id,
        name=class_.name,
        instructor_uid=class_.instructor_uid,
        instructor_name=current_user.display_name,
        join_code=class_.join_code,
        created_at=class_.created_at,
        joined_at=None,
        student_count=0,
        is_owner=True,
    )


@router.post("/join", response_model=ClassSummaryResponse, status_code=201)
async def join_class(
    body: JoinClassRequest,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):
    normalized_code = body.join_code.strip().upper()
    result = await db.execute(select(Class).where(Class.join_code == normalized_code))
    class_ = result.scalar_one_or_none()
    if not class_:
        raise NotFoundException("Class not found for that join code")

    membership_result = await db.execute(
        select(ClassMembership).where(
            ClassMembership.class_id == class_.class_id,
            ClassMembership.user_uid == current_user.uid,
        )
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None:
        membership = ClassMembership(
            class_id=class_.class_id,
            user_uid=current_user.uid,
        )
        db.add(membership)
        await db.commit()
        await db.refresh(membership)

    student_count = len(await get_class_student_uids(db, class_.class_id))
    instructor_result = await db.execute(select(User.display_name).where(User.uid == class_.instructor_uid))
    instructor_name = instructor_result.scalar_one_or_none()

    return ClassSummaryResponse(
        class_id=class_.class_id,
        name=class_.name,
        instructor_uid=class_.instructor_uid,
        instructor_name=instructor_name,
        join_code=None,
        created_at=class_.created_at,
        joined_at=membership.joined_at,
        student_count=student_count,
        is_owner=False,
    )


@router.get("/{class_id}/students", response_model=list[ClassStudentResponse])
async def list_class_students(
    class_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == "instructor":
        await get_owned_class(db, class_id, current_user.uid)
    else:
        await get_class_membership(db, class_id, current_user.uid)

    result = await db.execute(
        select(User.uid, User.display_name, ClassMembership.joined_at)
        .join(ClassMembership, ClassMembership.user_uid == User.uid)
        .where(
            ClassMembership.class_id == class_id,
            User.role == "student",
        )
        .order_by(User.display_name.asc())
    )

    return [
        ClassStudentResponse(
            uid=uid,
            display_name=display_name,
            joined_at=joined_at,
        )
        for uid, display_name, joined_at in result.all()
    ]


@router.delete("/{class_id}/members/me", status_code=204)
async def leave_class(
    class_id: str,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):
    membership = await get_class_membership(db, class_id, current_user.uid)

    exercise_ids = select(Exercise.exercise_id).where(Exercise.class_id == class_id)
    await db.execute(
        delete(ExerciseAssignment).where(
            ExerciseAssignment.student_uid == current_user.uid,
            ExerciseAssignment.exercise_id.in_(exercise_ids),
        )
    )
    await db.delete(membership)
    await db.commit()


@router.delete("/{class_id}/students/{student_uid}", status_code=204)
async def remove_student_from_class(
    class_id: str,
    student_uid: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_class(db, class_id, current_user.uid)
    membership = await get_class_membership(db, class_id, student_uid)

    student_result = await db.execute(select(User).where(User.uid == student_uid))
    student = student_result.scalar_one_or_none()
    if not student or student.role != "student":
        raise BadRequestException("Only student memberships can be removed")

    exercise_ids = select(Exercise.exercise_id).where(Exercise.class_id == class_id)
    await db.execute(
        delete(ExerciseAssignment).where(
            ExerciseAssignment.student_uid == student_uid,
            ExerciseAssignment.exercise_id.in_(exercise_ids),
        )
    )
    await db.delete(membership)
    await db.commit()


@router.post("/{class_id}/join-code/regenerate", response_model=JoinCodeResponse)
async def regenerate_join_code(
    class_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    class_ = await get_owned_class(db, class_id, current_user.uid)
    class_.join_code = await _create_unique_join_code(db)
    db.add(class_)
    await db.commit()
    await db.refresh(class_)

    return JoinCodeResponse(
        class_id=class_.class_id,
        join_code=class_.join_code,
    )

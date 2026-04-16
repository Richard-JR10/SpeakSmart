# app/api/v1/endpoints/exercises.py
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user, require_instructor, get_db
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from app.db.models.user import User
from app.db.models.phrase import Phrase
from app.db.models.exercise import Exercise, ExercisePhrase, ExerciseAssignment
from app.schemas.exercise import (
    ExerciseCreateRequest,
    ExerciseResponse,
    StudentExerciseResponse,
    ExerciseAssignmentResponse,
)

router = APIRouter(prefix="/exercises", tags=["exercises"])


# ── Instructor — create exercise ───────────────────────────────────────────────

@router.post("", response_model=ExerciseResponse, status_code=201)
async def create_exercise(
    body: ExerciseCreateRequest,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """
    Instructor only — creates a new exercise and assigns it
    to a list of students in one request.
    """

    # Validate all phrase_ids exist
    for phrase_id in body.phrase_ids:
        result = await db.execute(
            select(Phrase).where(Phrase.phrase_id == phrase_id)
        )
        if not result.scalar_one_or_none():
            raise BadRequestException(f"Phrase '{phrase_id}' not found")

    # Validate all student_uids exist
    for uid in body.student_uids:
        result = await db.execute(
            select(User).where(User.uid == uid, User.role == "student")
        )
        if not result.scalar_one_or_none():
            raise BadRequestException(f"Student '{uid}' not found")

    # Create the exercise
    exercise = Exercise(
        exercise_id=body.exercise_id,
        title=body.title,
        instructor_uid=current_user.uid,
        due_date=body.due_date,
    )
    db.add(exercise)
    await db.flush()  # Get exercise_id into DB before adding children

    # Link phrases
    for phrase_id in body.phrase_ids:
        db.add(ExercisePhrase(
            exercise_id=body.exercise_id,
            phrase_id=phrase_id,
        ))

    # Assign to students
    for uid in body.student_uids:
        db.add(ExerciseAssignment(
            exercise_id=body.exercise_id,
            student_uid=uid,
        ))

    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(Exercise)
        .options(
            selectinload(Exercise.phrases),
            selectinload(Exercise.assignments),
        )
        .where(Exercise.exercise_id == body.exercise_id)
    )
    return result.scalar_one()


# ── Instructor — assign existing exercise to more students ─────────────────────

@router.post("/{exercise_id}/assign", response_model=list[ExerciseAssignmentResponse])
async def assign_exercise(
    exercise_id: str,
    student_uids: list[str],
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """
    Instructor only — assigns an existing exercise to additional students.
    Skips students already assigned.
    """
    # Verify exercise exists and belongs to this instructor
    result = await db.execute(
        select(Exercise).where(Exercise.exercise_id == exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise NotFoundException(f"Exercise '{exercise_id}' not found")
    if exercise.instructor_uid != current_user.uid:
        raise ForbiddenException("You can only assign your own exercises")

    new_assignments = []
    for uid in student_uids:
        # Check not already assigned
        existing = await db.execute(
            select(ExerciseAssignment).where(
                ExerciseAssignment.exercise_id == exercise_id,
                ExerciseAssignment.student_uid == uid,
            )
        )
        if existing.scalar_one_or_none():
            continue  # Skip — already assigned

        assignment = ExerciseAssignment(
            exercise_id=exercise_id,
            student_uid=uid,
        )
        db.add(assignment)
        new_assignments.append(assignment)

    await db.commit()
    for a in new_assignments:
        await db.refresh(a)

    return new_assignments


# ── Instructor — get all exercises they created ────────────────────────────────

@router.get("/instructor/mine", response_model=list[ExerciseResponse])
async def get_my_exercises(
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Returns all exercises created by the current instructor."""
    result = await db.execute(
        select(Exercise)
        .options(
            selectinload(Exercise.phrases),
            selectinload(Exercise.assignments),
        )
        .where(Exercise.instructor_uid == current_user.uid)
        .order_by(Exercise.created_at.desc())
    )
    return result.scalars().all()


# ── Instructor — get single exercise detail ────────────────────────────────────

@router.get("/detail/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise_detail(
    exercise_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Returns full exercise detail including all assignments and phrases."""
    result = await db.execute(
        select(Exercise)
        .options(
            selectinload(Exercise.phrases),
            selectinload(Exercise.assignments),
        )
        .where(Exercise.exercise_id == exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise NotFoundException(f"Exercise '{exercise_id}' not found")
    if exercise.instructor_uid != current_user.uid:
        raise ForbiddenException("You can only view your own exercises")

    return exercise


# ── Student — get assigned exercises ──────────────────────────────────────────

@router.get("/student/{student_uid}", response_model=list[StudentExerciseResponse])
async def get_student_exercises(
    student_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all exercises assigned to a student.
    Students can only view their own. Instructors can view any student.
    """
    if current_user.role == "student" and current_user.uid != student_uid:
        raise ForbiddenException("Students can only view their own exercises")

    # Fetch assignments with their exercises
    assignments_result = await db.execute(
        select(ExerciseAssignment)
        .options(selectinload(ExerciseAssignment.exercise))
        .where(ExerciseAssignment.student_uid == student_uid)
        .order_by(ExerciseAssignment.assigned_at.desc())
    )
    assignments = assignments_result.scalars().all()

    now = datetime.now(timezone.utc)
    response = []

    for assignment in assignments:
        exercise = assignment.exercise

        # Fetch phrase IDs for this exercise
        phrases_result = await db.execute(
            select(ExercisePhrase.phrase_id).where(
                ExercisePhrase.exercise_id == exercise.exercise_id
            )
        )
        phrase_ids = [row[0] for row in phrases_result.all()]

        # Check if overdue
        is_overdue = (
            exercise.due_date is not None
            and exercise.due_date < now
            and assignment.completed_at is None
        )

        response.append(
            StudentExerciseResponse(
                exercise_id=exercise.exercise_id,
                title=exercise.title,
                due_date=exercise.due_date,
                assigned_at=assignment.assigned_at,
                completed_at=assignment.completed_at,
                is_overdue=is_overdue,
                phrase_ids=phrase_ids,
            )
        )

    return response


# ── Student — mark exercise as complete ───────────────────────────────────────

@router.patch("/{exercise_id}/complete", response_model=ExerciseAssignmentResponse)
async def mark_exercise_complete(
    exercise_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Student marks an assigned exercise as completed.
    Called automatically when all phrases in the exercise have been attempted.
    """
    result = await db.execute(
        select(ExerciseAssignment).where(
            ExerciseAssignment.exercise_id == exercise_id,
            ExerciseAssignment.student_uid == current_user.uid,
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFoundException("Exercise assignment not found")

    if assignment.completed_at:
        return assignment  # Already completed — return as-is

    assignment.completed_at = datetime.now(timezone.utc)
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    return assignment


# ── Instructor — delete exercise ───────────────────────────────────────────────

@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Instructor only — deletes an exercise and all its assignments."""
    result = await db.execute(
        select(Exercise).where(Exercise.exercise_id == exercise_id)
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise NotFoundException(f"Exercise '{exercise_id}' not found")
    if exercise.instructor_uid != current_user.uid:
        raise ForbiddenException("You can only delete your own exercises")

    await db.delete(exercise)
    await db.commit()
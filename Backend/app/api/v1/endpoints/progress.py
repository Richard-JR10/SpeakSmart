# app/api/v1/endpoints/progress.py
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ForbiddenException
from app.db.models.user import User
from app.db.models.attempt import Attempt
from app.db.models.progress import ProgressSummary
from app.db.models.phrase import Phrase
from app.schemas.progress import (
    ProgressSummaryResponse,
    StudentDashboard,
    WeeklyAccuracy,
)

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{student_uid}", response_model=StudentDashboard)
async def get_student_progress(
    student_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full student dashboard data:
      - Overall average accuracy
      - Total attempts
      - Streak days
      - Progress broken down by module
      - Weakest module
      - Weekly accuracy chart data (last 8 weeks)

    Students can only view their own progress.
    Instructors can view any student.
    """
    if current_user.role == "student" and current_user.uid != student_uid:
        raise ForbiddenException("Students can only view their own progress")

    # 1. Fetch all progress summaries for this student
    summaries_result = await db.execute(
        select(ProgressSummary)
        .where(ProgressSummary.student_uid == student_uid)
        .order_by(ProgressSummary.average_accuracy.asc())
    )
    summaries = summaries_result.scalars().all()

    # 2. Compute overall stats
    if summaries:
        overall_average = round(
            sum(s.average_accuracy for s in summaries) / len(summaries), 2
        )
        total_attempts = sum(s.total_attempts for s in summaries)
        streak_days = max(s.streak_days for s in summaries)
        weakest = summaries[0]  # Already sorted ascending
        weakest_module_id = weakest.module_id
        weakest_module_score = weakest.average_accuracy
    else:
        overall_average = 0.0
        total_attempts = 0
        streak_days = 0
        weakest_module_id = None
        weakest_module_score = None

    # 3. Weekly accuracy — last 8 weeks
    weekly_accuracy = await _get_weekly_accuracy(db, student_uid, weeks=8)

    return StudentDashboard(
        overall_average=overall_average,
        total_attempts=total_attempts,
        streak_days=streak_days,
        weakest_module_id=weakest_module_id,
        weakest_module_score=weakest_module_score,
        progress_by_module=[
            ProgressSummaryResponse.model_validate(s) for s in summaries
        ],
        weekly_accuracy=weekly_accuracy,
    )


@router.get("/{student_uid}/module/{module_id}", response_model=ProgressSummaryResponse)
async def get_module_progress(
    student_uid: str,
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns progress summary for a specific student + module pair."""
    if current_user.role == "student" and current_user.uid != student_uid:
        raise ForbiddenException("Students can only view their own progress")

    result = await db.execute(
        select(ProgressSummary).where(
            ProgressSummary.student_uid == student_uid,
            ProgressSummary.module_id == module_id,
        )
    )
    summary = result.scalar_one_or_none()

    if not summary:
        # Return zero-state if no attempts yet
        return ProgressSummaryResponse(
            id=0,
            student_uid=student_uid,
            module_id=module_id,
            average_accuracy=0.0,
            total_attempts=0,
            streak_days=0,
            last_attempted_at=None,
            updated_at=datetime.now(timezone.utc),
        )

    return summary


# ── Helper ─────────────────────────────────────────────────────────────────────

async def _get_weekly_accuracy(
    db: AsyncSession,
    student_uid: str,
    weeks: int = 8,
) -> list[WeeklyAccuracy]:
    """
    Computes average accuracy per week for the last N weeks.
    Returns a list ordered from oldest to newest for chart rendering.
    """
    now = datetime.now(timezone.utc)
    results = []

    for i in range(weeks - 1, -1, -1):
        week_start = (now - timedelta(weeks=i)).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=7)

        result = await db.execute(
            select(
                func.avg(Attempt.accuracy_score).label("avg_score"),
                func.count(Attempt.attempt_id).label("attempt_count"),
            ).where(
                Attempt.student_uid == student_uid,
                Attempt.attempted_at >= week_start,
                Attempt.attempted_at < week_end,
            )
        )
        row = result.one()

        results.append(
            WeeklyAccuracy(
                week_start=week_start.date().isoformat(),
                average_accuracy=round(float(row.avg_score or 0.0), 2),
                attempt_count=row.attempt_count or 0,
            )
        )

    return results
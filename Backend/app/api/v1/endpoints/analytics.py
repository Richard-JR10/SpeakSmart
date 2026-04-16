from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.dependencies import require_instructor, get_db
from app.core.exceptions import NotFoundException
from app.db.models.user import User
from app.db.models.attempt import Attempt
from app.db.models.progress import ProgressSummary
from app.schemas.analytics import (
    ClassOverview,
    StudentStat,
    StudentDrillDown,
    PhonemeErrorBreakdown,
    WeeklyClassAccuracy,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Students below this accuracy are flagged on the instructor dashboard
DEFAULT_FLAG_THRESHOLD = 60.0


# ── Class overview ─────────────────────────────────────────────────────────────

@router.get("/class/{class_id}", response_model=ClassOverview)
async def get_class_overview(
    class_id: str,
    flag_threshold: float = Query(default=DEFAULT_FLAG_THRESHOLD),
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full class-wide analytics overview for the
    instructor dashboard home screen.
    """

    # 1. Fetch all students in this class
    students_result = await db.execute(
        select(User).where(
            User.class_id == class_id,
            User.role == "student",
        )
    )
    students = students_result.scalars().all()

    if not students:
        raise NotFoundException(f"No students found for class '{class_id}'")

    student_uids = [s.uid for s in students]

    # 2. Fetch all progress summaries for these students
    summaries_result = await db.execute(
        select(ProgressSummary).where(
            ProgressSummary.student_uid.in_(student_uids)
        )
    )
    summaries = summaries_result.scalars().all()

    # 3. Build per-student stats
    student_stats = _build_student_stats(students, summaries, flag_threshold)

    # 4. Class-wide average
    all_averages = [s.overall_average for s in student_stats if s.total_attempts > 0]
    class_average = round(sum(all_averages) / len(all_averages), 2) if all_averages else 0.0

    # 5. This week's attempts + active students
    week_start = _get_week_start()
    weekly_result = await db.execute(
        select(
            func.count(Attempt.attempt_id).label("total"),
            func.count(func.distinct(Attempt.student_uid)).label("active"),
        ).where(
            Attempt.student_uid.in_(student_uids),
            Attempt.attempted_at >= week_start,
        )
    )
    weekly_row = weekly_result.one()
    weekly_attempts = weekly_row.total or 0
    active_students = weekly_row.active or 0

    # 6. Phoneme error breakdown (class-wide averages)
    phoneme_breakdown = await _get_phoneme_breakdown(db, student_uids)

    # 7. Weekly trend (last 8 weeks)
    weekly_trend = await _get_class_weekly_trend(db, student_uids, weeks=8)

    # 8. Flagged students
    flagged = [s for s in student_stats if s.is_flagged]

    return ClassOverview(
        class_id=class_id,
        total_students=len(students),
        active_students=active_students,
        weekly_attempts=weekly_attempts,
        class_average=class_average,
        flagged_students=flagged,
        phoneme_breakdown=phoneme_breakdown,
        weekly_trend=weekly_trend,
    )


# ── All students list ──────────────────────────────────────────────────────────

@router.get("/students/{class_id}", response_model=list[StudentStat])
async def get_all_students(
    class_id: str,
    flag_threshold: float = Query(default=DEFAULT_FLAG_THRESHOLD),
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full student table for the instructor dashboard —
    every student with their accuracy, attempts, streak, and flag status.
    """
    students_result = await db.execute(
        select(User).where(
            User.class_id == class_id,
            User.role == "student",
        ).order_by(User.display_name)
    )
    students = students_result.scalars().all()

    if not students:
        raise NotFoundException(f"No students found for class '{class_id}'")

    student_uids = [s.uid for s in students]

    summaries_result = await db.execute(
        select(ProgressSummary).where(
            ProgressSummary.student_uid.in_(student_uids)
        )
    )
    summaries = summaries_result.scalars().all()

    return _build_student_stats(students, summaries, flag_threshold)


# ── Individual student drill-down ──────────────────────────────────────────────

@router.get("/student/{student_uid}", response_model=StudentDrillDown)
async def get_student_drilldown(
    student_uid: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full drill-down view for a single student —
    phoneme breakdown, recent attempts, weakest module.
    """
    # Fetch student
    student_result = await db.execute(
        select(User).where(User.uid == student_uid)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise NotFoundException(f"Student '{student_uid}' not found")

    # Fetch progress summaries
    summaries_result = await db.execute(
        select(ProgressSummary)
        .where(ProgressSummary.student_uid == student_uid)
        .order_by(ProgressSummary.average_accuracy.asc())
    )
    summaries = summaries_result.scalars().all()

    # Overall stats
    if summaries:
        overall_average = round(
            sum(s.average_accuracy for s in summaries) / len(summaries), 2
        )
        total_attempts = sum(s.total_attempts for s in summaries)
        streak_days = max(s.streak_days for s in summaries)
        weakest = summaries[0]
        weakest_module_id = weakest.module_id
        weakest_module_score = weakest.average_accuracy
    else:
        overall_average = 0.0
        total_attempts = 0
        streak_days = 0
        weakest_module_id = None
        weakest_module_score = None

    # Phoneme breakdown
    phoneme_breakdown = await _get_phoneme_breakdown(db, [student_uid])

    # Recent 10 attempts
    attempts_result = await db.execute(
        select(Attempt)
        .where(Attempt.student_uid == student_uid)
        .order_by(Attempt.attempted_at.desc())
        .limit(10)
    )
    recent_attempts = [
        {
            "attempt_id": a.attempt_id,
            "phrase_id": a.phrase_id,
            "accuracy_score": a.accuracy_score,
            "mora_timing_score": a.mora_timing_score,
            "consonant_score": a.consonant_score,
            "vowel_score": a.vowel_score,
            "feedback_text": a.feedback_text,
            "attempted_at": a.attempted_at.isoformat(),
        }
        for a in attempts_result.scalars().all()
    ]

    return StudentDrillDown(
        uid=student.uid,
        display_name=student.display_name,
        email=student.email,
        overall_average=overall_average,
        total_attempts=total_attempts,
        streak_days=streak_days,
        phoneme_breakdown=phoneme_breakdown,
        weakest_module_id=weakest_module_id,
        weakest_module_score=weakest_module_score,
        recent_attempts=recent_attempts,
    )


# ── Phoneme heatmap ────────────────────────────────────────────────────────────

@router.get("/heatmap/{class_id}")
async def get_phoneme_heatmap(
    class_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns phoneme error rates per module for the heatmap view.
    Response is a dict keyed by module_id with phoneme averages.
    """
    students_result = await db.execute(
        select(User).where(
            User.class_id == class_id,
            User.role == "student",
        )
    )
    students = students_result.scalars().all()
    if not students:
        raise NotFoundException(f"No students found for class '{class_id}'")

    student_uids = [s.uid for s in students]

    # Get per-module phoneme averages
    result = await db.execute(
        select(
            ProgressSummary.module_id,
            func.avg(Attempt.mora_timing_score).label("mora_avg"),
            func.avg(Attempt.consonant_score).label("consonant_avg"),
            func.avg(Attempt.vowel_score).label("vowel_avg"),
            func.avg(Attempt.accuracy_score).label("overall_avg"),
        )
        .join(Attempt, Attempt.student_uid == ProgressSummary.student_uid)
        .where(ProgressSummary.student_uid.in_(student_uids))
        .group_by(ProgressSummary.module_id)
    )

    heatmap = {}
    for row in result.all():
        heatmap[row.module_id] = {
            "mora_timing_avg": round(float(row.mora_avg or 0), 2),
            "consonant_avg": round(float(row.consonant_avg or 0), 2),
            "vowel_avg": round(float(row.vowel_avg or 0), 2),
            "overall_avg": round(float(row.overall_avg or 0), 2),
        }

    return heatmap


# ── Internal helpers ───────────────────────────────────────────────────────────

def _build_student_stats(
    students: list[User],
    summaries: list[ProgressSummary],
    flag_threshold: float,
) -> list[StudentStat]:
    """Groups summaries by student and computes per-student stats."""

    # Group summaries by student_uid
    summaries_by_uid: dict[str, list[ProgressSummary]] = {}
    for s in summaries:
        summaries_by_uid.setdefault(s.student_uid, []).append(s)

    stats = []
    for student in students:
        student_summaries = summaries_by_uid.get(student.uid, [])

        if student_summaries:
            overall_average = round(
                sum(s.average_accuracy for s in student_summaries)
                / len(student_summaries),
                2,
            )
            total_attempts = sum(s.total_attempts for s in student_summaries)
            streak_days = max(s.streak_days for s in student_summaries)
            weakest = min(student_summaries, key=lambda s: s.average_accuracy)
            weakest_module_id = weakest.module_id
        else:
            overall_average = 0.0
            total_attempts = 0
            streak_days = 0
            weakest_module_id = None

        stats.append(
            StudentStat(
                uid=student.uid,
                display_name=student.display_name,
                email=student.email,
                overall_average=overall_average,
                total_attempts=total_attempts,
                streak_days=streak_days,
                weakest_module_id=weakest_module_id,
                is_flagged=overall_average < flag_threshold and total_attempts > 0,
            )
        )

    return stats


async def _get_phoneme_breakdown(
    db: AsyncSession,
    student_uids: list[str],
) -> PhonemeErrorBreakdown:
    """Computes class-wide or student-wide phoneme averages from attempts."""
    result = await db.execute(
        select(
            func.avg(Attempt.mora_timing_score).label("mora_avg"),
            func.avg(Attempt.consonant_score).label("consonant_avg"),
            func.avg(Attempt.vowel_score).label("vowel_avg"),
            func.avg(Attempt.accuracy_score).label("overall_avg"),
        ).where(Attempt.student_uid.in_(student_uids))
    )
    row = result.one()

    return PhonemeErrorBreakdown(
        mora_timing_avg=round(float(row.mora_avg or 0), 2),
        consonant_avg=round(float(row.consonant_avg or 0), 2),
        vowel_avg=round(float(row.vowel_avg or 0), 2),
        overall_avg=round(float(row.overall_avg or 0), 2),
    )


async def _get_class_weekly_trend(
    db: AsyncSession,
    student_uids: list[str],
    weeks: int = 8,
) -> list[WeeklyClassAccuracy]:
    """Computes week-by-week class accuracy for the trend chart."""
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
                func.count(func.distinct(Attempt.student_uid)).label("active_students"),
            ).where(
                Attempt.student_uid.in_(student_uids),
                Attempt.attempted_at >= week_start,
                Attempt.attempted_at < week_end,
            )
        )
        row = result.one()

        results.append(
            WeeklyClassAccuracy(
                week_start=week_start.date().isoformat(),
                average_accuracy=round(float(row.avg_score or 0.0), 2),
                attempt_count=row.attempt_count or 0,
                active_students=row.active_students or 0,
            )
        )

    return results


def _get_week_start() -> datetime:
    """Returns the start of the current week (Monday 00:00 UTC)."""
    now = datetime.now(timezone.utc)
    return (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
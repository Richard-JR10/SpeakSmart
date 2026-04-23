from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_class_student_uids,
    get_db,
    get_owned_class,
    require_instructor,
)
from app.core.exceptions import NotFoundException
from app.db.models.attempt import Attempt
from app.db.models.class_ import ClassMembership
from app.db.models.phrase import Phrase
from app.db.models.progress import ProgressSummary
from app.db.models.user import User
from app.schemas.analytics import (
    ClassOverview,
    PhonemeErrorBreakdown,
    StudentDrillDown,
    StudentStat,
    WeeklyClassAccuracy,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

DEFAULT_FLAG_THRESHOLD = 60.0


@router.get("/class/{class_id}", response_model=ClassOverview)
async def get_class_overview(
    class_id: str,
    flag_threshold: float = Query(default=DEFAULT_FLAG_THRESHOLD),
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_class(db, class_id, current_user.uid)
    students = await _get_students_for_class(db, class_id)
    student_uids = [student.uid for student in students]

    summaries = await _get_progress_summaries(db, student_uids)
    student_stats = _build_student_stats(students, summaries, flag_threshold)
    all_averages = [student.overall_average for student in student_stats if student.total_attempts > 0]
    class_average = round(sum(all_averages) / len(all_averages), 2) if all_averages else 0.0

    weekly_attempts = 0
    active_students = 0
    if student_uids:
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

    phoneme_breakdown = await _get_phoneme_breakdown(db, student_uids)
    weekly_trend = await _get_class_weekly_trend(db, student_uids, weeks=8)
    flagged = [student for student in student_stats if student.is_flagged]

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


@router.get("/students/{class_id}", response_model=list[StudentStat])
async def get_all_students(
    class_id: str,
    flag_threshold: float = Query(default=DEFAULT_FLAG_THRESHOLD),
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_class(db, class_id, current_user.uid)
    students = await _get_students_for_class(db, class_id)
    student_uids = [student.uid for student in students]
    summaries = await _get_progress_summaries(db, student_uids)
    return _build_student_stats(students, summaries, flag_threshold)


@router.get("/student/{student_uid}", response_model=StudentDrillDown)
async def get_student_drilldown(
    student_uid: str,
    class_id: str = Query(...),
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_class(db, class_id, current_user.uid)
    student_uids = await get_class_student_uids(db, class_id)
    if student_uid not in student_uids:
        raise NotFoundException(f"Student '{student_uid}' not found in class '{class_id}'")

    student_result = await db.execute(select(User).where(User.uid == student_uid))
    student = student_result.scalar_one_or_none()
    if not student:
        raise NotFoundException(f"Student '{student_uid}' not found")

    summaries_result = await db.execute(
        select(ProgressSummary)
        .where(ProgressSummary.student_uid == student_uid)
        .order_by(ProgressSummary.average_accuracy.asc())
    )
    summaries = summaries_result.scalars().all()

    if summaries:
        overall_average = round(
            sum(summary.average_accuracy for summary in summaries) / len(summaries),
            2,
        )
        total_attempts = sum(summary.total_attempts for summary in summaries)
        streak_days = max(summary.streak_days for summary in summaries)
        weakest = summaries[0]
        weakest_module_id = weakest.module_id
        weakest_module_score = weakest.average_accuracy
    else:
        overall_average = 0.0
        total_attempts = 0
        streak_days = 0
        weakest_module_id = None
        weakest_module_score = None

    phoneme_breakdown = await _get_phoneme_breakdown(db, [student_uid])

    attempts_result = await db.execute(
        select(Attempt)
        .where(Attempt.student_uid == student_uid)
        .order_by(Attempt.attempted_at.desc())
        .limit(10)
    )
    recent_attempts = [
        {
            "attempt_id": attempt.attempt_id,
            "phrase_id": attempt.phrase_id,
            "accuracy_score": attempt.accuracy_score,
            "mora_timing_score": attempt.mora_timing_score,
            "consonant_score": attempt.consonant_score,
            "vowel_score": attempt.vowel_score,
            "feedback_text": attempt.feedback_text,
            "verification_status": attempt.verification_status,
            "recognized_phrase_id": attempt.recognized_phrase_id,
            "recognized_text": attempt.recognized_text,
            "recognized_text_romaji": attempt.recognized_text_romaji,
            "counts_for_progress": attempt.counts_for_progress,
            "attempted_at": attempt.attempted_at.isoformat(),
        }
        for attempt in attempts_result.scalars().all()
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


@router.get("/heatmap/{class_id}")
async def get_phoneme_heatmap(
    class_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_class(db, class_id, current_user.uid)
    student_uids = await get_class_student_uids(db, class_id)
    if not student_uids:
        return {}

    result = await db.execute(
        select(
            Phrase.module_id,
            func.avg(Attempt.mora_timing_score).label("mora_avg"),
            func.avg(Attempt.consonant_score).label("consonant_avg"),
            func.avg(Attempt.vowel_score).label("vowel_avg"),
            func.avg(Attempt.accuracy_score).label("overall_avg"),
        )
        .join(Phrase, Phrase.phrase_id == Attempt.phrase_id)
        .where(
            Attempt.student_uid.in_(student_uids),
            Attempt.counts_for_progress.is_(True),
        )
        .group_by(Phrase.module_id)
    )

    heatmap: dict[str, dict[str, float]] = {}
    for row in result.all():
        heatmap[row.module_id] = {
            "mora_timing_avg": round(float(row.mora_avg or 0), 2),
            "consonant_avg": round(float(row.consonant_avg or 0), 2),
            "vowel_avg": round(float(row.vowel_avg or 0), 2),
            "overall_avg": round(float(row.overall_avg or 0), 2),
        }

    return heatmap


async def _get_students_for_class(
    db: AsyncSession,
    class_id: str,
) -> list[User]:
    result = await db.execute(
        select(User)
        .join(ClassMembership, ClassMembership.user_uid == User.uid)
        .where(
            ClassMembership.class_id == class_id,
            User.role == "student",
        )
        .order_by(User.display_name)
    )
    return result.scalars().all()


async def _get_progress_summaries(
    db: AsyncSession,
    student_uids: list[str],
) -> list[ProgressSummary]:
    if not student_uids:
        return []

    result = await db.execute(
        select(ProgressSummary).where(ProgressSummary.student_uid.in_(student_uids))
    )
    return result.scalars().all()


def _build_student_stats(
    students: list[User],
    summaries: list[ProgressSummary],
    flag_threshold: float,
) -> list[StudentStat]:
    summaries_by_uid: dict[str, list[ProgressSummary]] = {}
    for summary in summaries:
        summaries_by_uid.setdefault(summary.student_uid, []).append(summary)

    stats: list[StudentStat] = []
    for student in students:
        student_summaries = summaries_by_uid.get(student.uid, [])

        if student_summaries:
            overall_average = round(
                sum(summary.average_accuracy for summary in student_summaries)
                / len(student_summaries),
                2,
            )
            total_attempts = sum(summary.total_attempts for summary in student_summaries)
            streak_days = max(summary.streak_days for summary in student_summaries)
            weakest = min(student_summaries, key=lambda summary: summary.average_accuracy)
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
    if not student_uids:
        return PhonemeErrorBreakdown(
            mora_timing_avg=0.0,
            consonant_avg=0.0,
            vowel_avg=0.0,
            overall_avg=0.0,
        )

    result = await db.execute(
        select(
            func.avg(Attempt.mora_timing_score).label("mora_avg"),
            func.avg(Attempt.consonant_score).label("consonant_avg"),
            func.avg(Attempt.vowel_score).label("vowel_avg"),
            func.avg(Attempt.accuracy_score).label("overall_avg"),
        ).where(
            Attempt.student_uid.in_(student_uids),
            Attempt.counts_for_progress.is_(True),
        )
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
    now = datetime.now(timezone.utc)
    results: list[WeeklyClassAccuracy] = []

    for index in range(weeks - 1, -1, -1):
        week_start = (now - timedelta(weeks=index)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ) - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=7)

        average_accuracy = 0.0
        attempt_count = 0
        active_students = 0
        if student_uids:
            result = await db.execute(
                select(
                    func.avg(Attempt.accuracy_score).label("avg_score"),
                    func.count(Attempt.attempt_id).label("attempt_count"),
                    func.count(func.distinct(Attempt.student_uid)).label("active_students"),
                ).where(
                    Attempt.student_uid.in_(student_uids),
                    Attempt.counts_for_progress.is_(True),
                    Attempt.attempted_at >= week_start,
                    Attempt.attempted_at < week_end,
                )
            )
            row = result.one()
            average_accuracy = round(float(row.avg_score or 0.0), 2)
            attempt_count = row.attempt_count or 0
            active_students = row.active_students or 0

        results.append(
            WeeklyClassAccuracy(
                week_start=week_start.date().isoformat(),
                average_accuracy=average_accuracy,
                attempt_count=attempt_count,
                active_students=active_students,
            )
        )

    return results


def _get_week_start() -> datetime:
    now = datetime.now(timezone.utc)
    return (now - timedelta(days=now.weekday())).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

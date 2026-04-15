# app/services/progress.py
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models.attempt import Attempt
from app.db.models.progress import ProgressSummary


async def update_progress_summary(
    db: AsyncSession,
    student_uid: str,
    module_id: str,
) -> ProgressSummary:
    """
    Recalculates and upserts the progress summary for a student/module pair.
    Called automatically after every attempt is saved.
    """

    # Fetch all attempts for this student + module
    result = await db.execute(
        select(Attempt)
        .join(Attempt.phrase)
        .where(
            Attempt.student_uid == student_uid,
            Attempt.phrase.has(module_id=module_id),
        )
        .order_by(Attempt.attempted_at.desc())
    )
    attempts = result.scalars().all()

    if not attempts:
        return None

    # Compute average accuracy
    average_accuracy = round(
        sum(a.accuracy_score for a in attempts) / len(attempts), 2
    )
    total_attempts = len(attempts)
    last_attempted_at = attempts[0].attempted_at

    # Compute streak — consecutive days with at least one attempt
    streak_days = _compute_streak(attempts)

    # Fetch existing summary or create new
    summary_result = await db.execute(
        select(ProgressSummary).where(
            ProgressSummary.student_uid == student_uid,
            ProgressSummary.module_id == module_id,
        )
    )
    summary = summary_result.scalar_one_or_none()

    if summary:
        summary.average_accuracy = average_accuracy
        summary.total_attempts = total_attempts
        summary.streak_days = streak_days
        summary.last_attempted_at = last_attempted_at
        summary.updated_at = datetime.now(timezone.utc)
    else:
        summary = ProgressSummary(
            student_uid=student_uid,
            module_id=module_id,
            average_accuracy=average_accuracy,
            total_attempts=total_attempts,
            streak_days=streak_days,
            last_attempted_at=last_attempted_at,
        )
        db.add(summary)

    await db.commit()
    await db.refresh(summary)
    return summary


def _compute_streak(attempts: list[Attempt]) -> int:
    """
    Counts consecutive days ending today (or yesterday)
    where at least one attempt was made.
    """
    if not attempts:
        return 0

    # Get unique attempt dates in descending order
    attempt_dates = sorted(
        set(a.attempted_at.date() for a in attempts),
        reverse=True,
    )

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    # Streak must include today or yesterday to be active
    if attempt_dates[0] < yesterday:
        return 0

    streak = 1
    for i in range(1, len(attempt_dates)):
        if (attempt_dates[i - 1] - attempt_dates[i]).days == 1:
            streak += 1
        else:
            break

    return streak
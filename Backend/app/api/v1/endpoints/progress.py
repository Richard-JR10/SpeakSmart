# app/api/v1/endpoints/progress.py
import asyncio
from datetime import datetime, timezone, timedelta
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct

from app.config import settings
from app.core.dependencies import authorize_student_access, get_current_user, get_db
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.limiter import limiter
from app.db.models.module import Module
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

_MODULE_TEMPLATES: dict[str, str] = {
    "module_greetings": "certificate_greetings.pdf",
    "module_hotel": "certificate_hotel.pdf",
    "module_directions": "certificate_directions.pdf",
    "module_food": "certificate_food.pdf",
    "module_emergency": "certificate_emergency.pdf",
    "module_tour_guide": "certificate_tour_guide.pdf",
}


@router.get("/{student_uid}", response_model=StudentDashboard)
@limiter.limit(settings.RATE_LIMIT_PROGRESS)
async def get_student_progress(
    request: Request,
    student_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full student dashboard data:
      - Overall average accuracy
      - Total attempts
      - Streak days
      - Progress broken down by module (includes completed_phrases / total_phrases)
      - Weakest module
      - Weekly accuracy chart data (last 8 weeks)

    Students can only view their own progress.
    Instructors can view students in their classes.
    """
    await authorize_student_access(db, current_user, student_uid)

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

        module_ids = [s.module_id for s in summaries]

        # 3a. Batch: completed phrases per module (distinct phrase_ids with counts_for_progress=True)
        completed_result = await db.execute(
            select(
                Phrase.module_id,
                func.count(distinct(Attempt.phrase_id)).label("completed_count"),
            )
            .join(Attempt, Attempt.phrase_id == Phrase.phrase_id)
            .where(
                Attempt.student_uid == student_uid,
                Attempt.counts_for_progress.is_(True),
                Phrase.module_id.in_(module_ids),
            )
            .group_by(Phrase.module_id)
        )
        completed_by_module = {
            row.module_id: row.completed_count for row in completed_result.all()
        }

        # 3b. Batch: total phrases per module
        total_result = await db.execute(
            select(
                Phrase.module_id,
                func.count(Phrase.phrase_id).label("total_count"),
            )
            .where(Phrase.module_id.in_(module_ids))
            .group_by(Phrase.module_id)
        )
        total_by_module = {
            row.module_id: row.total_count for row in total_result.all()
        }

        progress_by_module = [
            ProgressSummaryResponse(
                id=s.id,
                student_uid=s.student_uid,
                module_id=s.module_id,
                average_accuracy=s.average_accuracy,
                total_attempts=s.total_attempts,
                streak_days=s.streak_days,
                last_attempted_at=s.last_attempted_at,
                updated_at=s.updated_at,
                completed_phrases=completed_by_module.get(s.module_id, 0),
                total_phrases=total_by_module.get(s.module_id, 0),
            )
            for s in summaries
        ]
    else:
        overall_average = 0.0
        total_attempts = 0
        streak_days = 0
        weakest_module_id = None
        weakest_module_score = None
        progress_by_module = []

    # 4. Weekly accuracy — last 8 weeks
    weekly_accuracy = await _get_weekly_accuracy(db, student_uid, weeks=8)

    return StudentDashboard(
        overall_average=overall_average,
        total_attempts=total_attempts,
        streak_days=streak_days,
        weakest_module_id=weakest_module_id,
        weakest_module_score=weakest_module_score,
        progress_by_module=progress_by_module,
        weekly_accuracy=weekly_accuracy,
    )


@router.get("/{student_uid}/module/{module_id}/certificate")
@limiter.limit(settings.RATE_LIMIT_PROGRESS)
async def get_module_certificate(
    request: Request,
    student_uid: str,
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates and streams a filled certificate PDF for a completed module.
    Requires completed_phrases == total_phrases > 0.
    Students can only download their own certificates.
    Instructors can download certificates for students in their classes.
    """
    await authorize_student_access(db, current_user, student_uid)

    student_result = await db.execute(select(User).where(User.uid == student_uid))
    student = student_result.scalar_one_or_none()
    if not student:
        raise NotFoundException("Student not found")

    module_result = await db.execute(select(Module).where(Module.module_id == module_id))
    module = module_result.scalar_one_or_none()
    if not module:
        raise NotFoundException("Module not found")

    completed_result = await db.execute(
        select(func.count(distinct(Attempt.phrase_id)))
        .join(Phrase, Phrase.phrase_id == Attempt.phrase_id)
        .where(
            Attempt.student_uid == student_uid,
            Attempt.counts_for_progress.is_(True),
            Phrase.module_id == module_id,
        )
    )
    completed_phrases = completed_result.scalar() or 0

    total_result = await db.execute(
        select(func.count(Phrase.phrase_id)).where(Phrase.module_id == module_id)
    )
    total_phrases = total_result.scalar() or 0

    if total_phrases == 0 or completed_phrases < total_phrases:
        raise BadRequestException(
            "Certificate is only available when all phrases in the module are completed."
        )

    template_name = _MODULE_TEMPLATES.get(module_id)
    if not template_name:
        raise NotFoundException(f"No certificate template configured for module '{module_id}'")

    template_path = Path(__file__).parents[4] / "templates" / template_name
    if not template_path.exists():
        raise NotFoundException("Certificate template file not found on server")

    date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

    def _fill_pdf(path: Path, name: str, date: str) -> BytesIO:
        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(str(path))
        page = reader.pages[0]
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)

        overlay_bytes = _build_text_overlay(name, date, w, h)
        overlay_reader = PdfReader(BytesIO(overlay_bytes))

        writer = PdfWriter(clone_from=reader)
        writer.pages[0].merge_page(overlay_reader.pages[0])

        buf = BytesIO()
        writer.write(buf)
        buf.seek(0)
        return buf

    buffer = await asyncio.to_thread(_fill_pdf, template_path, student.display_name, date_str)

    module_slug = module_id.removeprefix("module_")
    filename = f"{module_slug}_certificate.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{student_uid}/module/{module_id}/completed-phrases")
@limiter.limit(settings.RATE_LIMIT_PROGRESS)
async def get_module_completed_phrases(
    request: Request,
    student_uid: str,
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Returns the list of phrase IDs that count toward module completion for this student.
    Uses the same query as completed_phrases in the progress summary.
    """
    await authorize_student_access(db, current_user, student_uid)

    result = await db.execute(
        select(distinct(Attempt.phrase_id))
        .join(Phrase, Phrase.phrase_id == Attempt.phrase_id)
        .where(
            Attempt.student_uid == student_uid,
            Attempt.counts_for_progress.is_(True),
            Phrase.module_id == module_id,
        )
    )
    return {"completed_phrase_ids": [row[0] for row in result.all()]}


@router.get("/{student_uid}/module/{module_id}", response_model=ProgressSummaryResponse)
@limiter.limit(settings.RATE_LIMIT_PROGRESS)
async def get_module_progress(
    request: Request,
    student_uid: str,
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns progress summary for a specific student + module pair."""
    await authorize_student_access(db, current_user, student_uid)

    # Compute phrase counts unconditionally so both zero-state and found paths return them
    completed_result = await db.execute(
        select(func.count(distinct(Attempt.phrase_id)))
        .join(Phrase, Phrase.phrase_id == Attempt.phrase_id)
        .where(
            Attempt.student_uid == student_uid,
            Attempt.counts_for_progress.is_(True),
            Phrase.module_id == module_id,
        )
    )
    completed_phrases = completed_result.scalar() or 0

    total_result = await db.execute(
        select(func.count(Phrase.phrase_id)).where(Phrase.module_id == module_id)
    )
    total_phrases = total_result.scalar() or 0

    result = await db.execute(
        select(ProgressSummary).where(
            ProgressSummary.student_uid == student_uid,
            ProgressSummary.module_id == module_id,
        )
    )
    summary = result.scalar_one_or_none()

    if not summary:
        return ProgressSummaryResponse(
            id=0,
            student_uid=student_uid,
            module_id=module_id,
            average_accuracy=0.0,
            total_attempts=0,
            streak_days=0,
            last_attempted_at=None,
            updated_at=datetime.now(timezone.utc),
            completed_phrases=completed_phrases,
            total_phrases=total_phrases,
        )

    return ProgressSummaryResponse(
        id=summary.id,
        student_uid=summary.student_uid,
        module_id=summary.module_id,
        average_accuracy=summary.average_accuracy,
        total_attempts=summary.total_attempts,
        streak_days=summary.streak_days,
        last_attempted_at=summary.last_attempted_at,
        updated_at=summary.updated_at,
        completed_phrases=completed_phrases,
        total_phrases=total_phrases,
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_text_overlay(name: str, date_str: str, width: float, height: float) -> bytes:
    """
    Build a minimal valid PDF containing only the student name and date text.

    Coordinates are in standard PDF page space (origin bottom-left, y up).
    Calibrated from the certificate template's XObject CTM [0.24, 0, 0, -0.24, 0, 604.08]:
      - Name blank: between separator at y≈319 and "presented to" at y≈425 → centre y=370
      - Date: same line as "Date of Completion:" label which maps to y≈171; label ends ~x=445
    """
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    name_font_size = 30
    name_approx_width = len(name) * name_font_size * 0.50
    name_x = max(80.0, (width - name_approx_width) / 2)
    name_y = 348.0

    date_x = 445.0
    date_y = 171.0
    date_font_size = 14

    stream = (
        f"BT /F1 {name_font_size} Tf {name_x:.2f} {name_y:.2f} Td ({esc(name)}) Tj ET\n"
        f"BT /F2 {date_font_size} Tf {date_x:.2f} {date_y:.2f} Td ({esc(date_str)}) Tj ET"
    )
    sb = stream.encode("latin-1")

    objs: list[bytes] = [
        b"1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n",
        b"2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n",
        (
            f"3 0 obj\n<</Type/Page/Parent 2 0 R"
            f"/MediaBox[0 0 {width:.2f} {height:.2f}]"
            f"/Contents 4 0 R/Resources<</Font<</F1 5 0 R/F2 6 0 R>>>>>>\nendobj\n"
        ).encode(),
        f"4 0 obj\n<</Length {len(sb)}>>\nstream\n".encode()
        + sb
        + b"\nendstream\nendobj\n",
        b"5 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica-BoldOblique>>\nendobj\n",
        b"6 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n",
    ]

    pdf = b"%PDF-1.4\n"
    offsets: list[int] = []
    for obj in objs:
        offsets.append(len(pdf))
        pdf += obj

    xref_pos = len(pdf)
    n = len(objs) + 1
    xref = f"xref\n0 {n}\n0000000000 65535 f \n"
    xref += "".join(f"{o:010d} 00000 n \n" for o in offsets)
    pdf += xref.encode()
    pdf += (
        f"trailer\n<</Size {n}/Root 1 0 R>>\nstartxref\n{xref_pos}\n%%EOF\n"
    ).encode()
    return pdf


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
                Attempt.counts_for_progress.is_(True),
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

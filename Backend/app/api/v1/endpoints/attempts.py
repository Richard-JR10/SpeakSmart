# app/api/v1/endpoints/attempts.py
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_current_user, require_instructor, get_db
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from app.db.models.user import User
from app.db.models.phrase import Phrase
from app.db.models.attempt import Attempt
from app.schemas.attempt import AttemptResponse, AttemptSummary
from app.services.r2_storage import upload_audio, download_audio, get_object_key_from_url
from app.services.scoring import score_attempt
from app.services.speech import validate_audio
from app.config import settings
from app.services.progress import update_progress_summary

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("", response_model=AttemptResponse, status_code=201)
async def submit_attempt(
    phrase_id: str = Form(...),
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Core endpoint — receives student audio, scores it, saves result.

    Flow:
      1. Validate audio file
      2. Fetch phrase + reference audio URL from DB
      3. Download reference audio from R2
      4. Run scoring pipeline
      5. Upload student audio to R2
      6. Save attempt to PostgreSQL
      7. Return scored result
    """

    # 1. Read and validate audio
    audio_bytes = await audio_file.read()

    try:
        validate_audio(audio_bytes, max_size_mb=settings.MAX_AUDIO_SIZE_MB)
    except ValueError as e:
        raise BadRequestException(str(e))

    # 2. Fetch phrase from DB
    phrase_result = await db.execute(
        select(Phrase).where(Phrase.phrase_id == phrase_id)
    )
    phrase = phrase_result.scalar_one_or_none()
    if not phrase:
        raise NotFoundException(f"Phrase '{phrase_id}' not found")

    if not phrase.reference_audio_url:
        raise BadRequestException(
            f"Phrase '{phrase_id}' has no reference audio — run the seeder first"
        )

    # 3. Download reference audio from R2 into memory
    try:
        ref_object_key = get_object_key_from_url(phrase.reference_audio_url)
        reference_audio = download_audio(ref_object_key)
    except RuntimeError as e:
        raise BadRequestException(f"Could not fetch reference audio: {e}")

    # 4. Run scoring pipeline
    try:
        scores = score_attempt(audio_bytes, reference_audio)
    except Exception as e:
        raise BadRequestException(f"Scoring failed: {e}")

    # 5. Upload student audio to R2
    attempt_id = str(uuid.uuid4())
    student_object_key = f"student-audio/{current_user.uid}/{attempt_id}.wav"

    try:
        audio_url = upload_audio(audio_bytes, student_object_key)
    except RuntimeError as e:
        raise BadRequestException(f"Audio upload failed: {e}")

    # 6. Save attempt to DB
    attempt = Attempt(
        attempt_id=attempt_id,
        student_uid=current_user.uid,
        phrase_id=phrase_id,
        audio_file_url=audio_url,
        accuracy_score=scores["accuracy_score"],
        mora_timing_score=scores["mora_timing_score"],
        consonant_score=scores["consonant_score"],
        vowel_score=scores["vowel_score"],
        phoneme_error_map=scores["phoneme_error_map"],
        feedback_text=scores["feedback_text"],
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    await update_progress_summary(
        db=db,
        student_uid=current_user.uid,
        module_id=phrase.module_id,
    )
    
    return attempt


@router.get("/{student_uid}", response_model=list[AttemptSummary])
async def get_attempts(
    student_uid: str,
    phrase_id: str | None = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns attempt history for a student.

    - Students can only fetch their own attempts.
    - Instructors can fetch any student's attempts.
    - Optionally filter by phrase_id.
    - Limited to last 20 by default.
    """
    # Access control
    if current_user.role == "student" and current_user.uid != student_uid:
        raise ForbiddenException("Students can only view their own attempts")

    query = (
        select(Attempt)
        .where(Attempt.student_uid == student_uid)
        .order_by(Attempt.attempted_at.desc())
        .limit(limit)
    )

    if phrase_id:
        query = query.where(Attempt.phrase_id == phrase_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{student_uid}/{attempt_id}", response_model=AttemptResponse)
async def get_attempt_detail(
    student_uid: str,
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns full detail for a single attempt including phoneme error map.
    Students can only view their own. Instructors can view any.
    """
    if current_user.role == "student" and current_user.uid != student_uid:
        raise ForbiddenException("Students can only view their own attempts")

    result = await db.execute(
        select(Attempt).where(
            Attempt.attempt_id == attempt_id,
            Attempt.student_uid == student_uid,
        )
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise NotFoundException("Attempt not found")

    return attempt
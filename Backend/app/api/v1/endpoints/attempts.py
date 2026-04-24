# app/api/v1/endpoints/attempts.py
import logging
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import authorize_student_access, get_current_user, get_db
from app.core.exceptions import NotFoundException, BadRequestException
from app.db.models.user import User
from app.db.models.phrase import Phrase
from app.db.models.attempt import Attempt
from app.schemas.attempt import AttemptResponse, AttemptSummary
from app.services.pronunciation import build_reference_target_from_phrase, get_pronunciation_overrides
from app.services.r2_storage import upload_audio, download_audio, get_object_key_from_url
from app.services.scoring import empty_score_payload, score_attempt
from app.services.speech import validate_audio
from app.services.verification import (
    VERIFICATION_ACCEPTED,
    VERIFICATION_NO_CLEAR_SPEECH,
    VERIFICATION_RETRY,
    VERIFICATION_WRONG_PHRASE,
    verify_phrase_audio,
)
from app.config import settings
from app.services.progress import update_progress_summary

router = APIRouter(prefix="/attempts", tags=["attempts"])
logger = logging.getLogger("speaksmart.attempts")
logger.setLevel(logging.INFO)


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

    module_phrase_rows = await db.execute(
        select(Phrase.phrase_id, Phrase.japanese_text).where(
            Phrase.module_id == phrase.module_id
        )
    )
    verification_candidate_rows = list(module_phrase_rows.all())
    verification_candidates = [
        (row.phrase_id, row.japanese_text)
        for row in verification_candidate_rows
    ]

    try:
        verification = verify_phrase_audio(
            audio_bytes=audio_bytes,
            target_phrase_id=phrase.phrase_id,
            target_text=phrase.japanese_text,
            candidate_pairs=verification_candidates,
        )
    except Exception as e:
        raise BadRequestException(f"Verification failed: {e}")

    logger.info(
        "attempt verification student=%s phrase=%s status=%s recognized_phrase=%s confidence=%s margin=%s recognized_text=%s",
        current_user.uid,
        phrase.phrase_id,
        verification.status,
        verification.recognized_phrase_id,
        verification.verification_confidence,
        verification.verification_margin,
        verification.recognized_text,
    )

    pronunciation_target = build_reference_target_from_phrase(phrase)
    pronunciation_overrides = get_pronunciation_overrides(phrase)

    # 4. Run scoring pipeline for accepted phrases only
    try:
        if verification.status == VERIFICATION_ACCEPTED:
            scores = score_attempt(
                audio_bytes,
                reference_audio,
                target_text=phrase.japanese_text,
                target_romaji=phrase.romaji,
                pronunciation_overrides=pronunciation_overrides,
                target_pronunciation=pronunciation_target,
            )
        else:
            scores = empty_score_payload(
                _build_verification_feedback(
                    verification.status,
                    verification.recognized_text_romaji,
                ),
                target_pronunciation=pronunciation_target,
                pronunciation_feedback=[],
            )
    except Exception as e:
        raise BadRequestException(f"Scoring failed: {e}")

    logger.info(
        "attempt scoring student=%s phrase=%s verification_status=%s score=%.2f mora=%.2f consonant=%.2f vowel=%.2f counts_for_progress=%s",
        current_user.uid,
        phrase.phrase_id,
        verification.status,
        scores["accuracy_score"],
        scores["mora_timing_score"],
        scores["consonant_score"],
        scores["vowel_score"],
        verification.status == VERIFICATION_ACCEPTED,
    )

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
        verification_status=verification.status,
        recognized_phrase_id=verification.recognized_phrase_id,
        recognized_text=verification.recognized_text,
        recognized_text_romaji=verification.recognized_text_romaji,
        target_pronunciation=scores["target_pronunciation"],
        pronunciation_feedback=scores["pronunciation_feedback"],
        verification_confidence=verification.verification_confidence,
        verification_margin=verification.verification_margin,
        counts_for_progress=verification.status == VERIFICATION_ACCEPTED,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    if attempt.counts_for_progress:
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
    - Instructors can fetch attempts for students in their classes.
    - Optionally filter by phrase_id.
    - Limited to last 20 by default.
    """
    await authorize_student_access(db, current_user, student_uid)

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
    Students can only view their own. Instructors can view students in their classes.
    """
    await authorize_student_access(db, current_user, student_uid)

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


def _build_verification_feedback(
    status: str,
    recognized_text_romaji: str | None,
) -> str:
    if status == VERIFICATION_NO_CLEAR_SPEECH:
        return "We could not detect enough clear speech in this recording. Please try again in a quieter spot."
    if status == VERIFICATION_RETRY:
        if recognized_text_romaji:
            return f"Phrase verification was uncertain for this recording. Whisper heard: {recognized_text_romaji}. Please try the target phrase again."
        return "Phrase verification was uncertain for this recording. Please try the target phrase again."
    if status == VERIFICATION_WRONG_PHRASE:
        if recognized_text_romaji:
            return f"We detected a different phrase than the target. Recognized text: {recognized_text_romaji}"
        return "We detected a different phrase than the target. Please try the assigned phrase again."
    if recognized_text_romaji:
        return f"We detected a different phrase than the target. Recognized text: {recognized_text_romaji}"
    return "We detected a different phrase than the target. Please try the assigned phrase again."

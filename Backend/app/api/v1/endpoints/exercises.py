import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import (
    authorize_student_access,
    get_class_student_uids,
    get_current_user,
    get_db,
    get_owned_class,
    require_instructor,
    require_student,
)
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.db.models.exercise import Exercise, ExerciseAssignment, ExercisePhrase, ExerciseSubmission
from app.db.models.phrase import Phrase
from app.db.models.user import User
from app.schemas.assignment_submission import (
    AssignmentSubmissionResponse,
    InstructorAssignmentSubmissionResponse,
    ReviewAssignmentSubmissionRequest,
    StudentAssignmentResponse,
    AssignmentPhraseStatus,
)
from app.schemas.exercise import (
    ExerciseAssignmentResponse,
    ExerciseCreateRequest,
    ExerciseResponse,
    StudentExerciseResponse,
)
from app.services.pronunciation import build_reference_target_from_phrase, get_pronunciation_overrides
from app.services.r2_storage import download_audio, get_object_key_from_url, upload_audio
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

router = APIRouter(prefix="/exercises", tags=["exercises"])
logger = logging.getLogger("speaksmart.exercises")
logger.setLevel(logging.INFO)


@router.post("", response_model=ExerciseResponse, status_code=201)
async def create_exercise(
    body: ExerciseCreateRequest,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_class(db, body.class_id, current_user.uid)
    await _validate_phrase_ids(db, body.phrase_ids)
    await _validate_student_memberships(db, body.class_id, body.student_uids)

    exercise = Exercise(
        exercise_id=body.exercise_id,
        class_id=body.class_id,
        title=body.title,
        instructor_uid=current_user.uid,
        due_date=body.due_date,
    )
    db.add(exercise)
    await db.flush()

    for phrase_id in body.phrase_ids:
        db.add(
            ExercisePhrase(
                exercise_id=body.exercise_id,
                phrase_id=phrase_id,
            )
        )

    for student_uid in body.student_uids:
        db.add(
            ExerciseAssignment(
                exercise_id=body.exercise_id,
                student_uid=student_uid,
            )
        )

    await db.commit()

    result = await db.execute(
        select(Exercise)
        .options(
            selectinload(Exercise.phrases),
            selectinload(Exercise.assignments),
        )
        .where(Exercise.exercise_id == body.exercise_id)
    )
    return result.scalar_one()


@router.post("/{exercise_id}/assign", response_model=list[ExerciseAssignmentResponse])
async def assign_exercise(
    exercise_id: str,
    student_uids: list[str],
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    exercise = await _get_owned_exercise(db, exercise_id, current_user.uid)
    if not exercise.class_id:
        raise BadRequestException("Exercise is missing a class assignment")

    await _validate_student_memberships(db, exercise.class_id, student_uids)

    new_assignments: list[ExerciseAssignment] = []
    for student_uid in student_uids:
        existing = await db.execute(
            select(ExerciseAssignment).where(
                ExerciseAssignment.exercise_id == exercise_id,
                ExerciseAssignment.student_uid == student_uid,
            )
        )
        if existing.scalar_one_or_none():
            continue

        assignment = ExerciseAssignment(
            exercise_id=exercise_id,
            student_uid=student_uid,
        )
        db.add(assignment)
        new_assignments.append(assignment)

    await db.commit()
    for assignment in new_assignments:
        await db.refresh(assignment)

    return new_assignments


@router.get("/instructor/mine", response_model=list[ExerciseResponse])
async def get_my_exercises(
    class_id: str = Query(...),
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_class(db, class_id, current_user.uid)
    result = await db.execute(
        select(Exercise)
        .options(
            selectinload(Exercise.phrases),
            selectinload(Exercise.assignments),
        )
        .where(
            Exercise.instructor_uid == current_user.uid,
            Exercise.class_id == class_id,
        )
        .order_by(Exercise.created_at.desc())
    )
    return result.scalars().all()


@router.get("/detail/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise_detail(
    exercise_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    return await _get_owned_exercise(db, exercise_id, current_user.uid, with_relationships=True)


@router.get("/student/{student_uid}", response_model=list[StudentExerciseResponse])
async def get_student_exercises(
    student_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await authorize_student_access(db, current_user, student_uid)

    assignments_result = await db.execute(
        select(ExerciseAssignment)
        .options(selectinload(ExerciseAssignment.exercise))
        .where(ExerciseAssignment.student_uid == student_uid)
        .order_by(ExerciseAssignment.assigned_at.desc())
    )
    assignments = assignments_result.scalars().all()

    now = datetime.now(timezone.utc)
    response: list[StudentExerciseResponse] = []

    for assignment in assignments:
        exercise = assignment.exercise
        if exercise is None:
            continue

        phrases_result = await db.execute(
            select(ExercisePhrase.phrase_id).where(
                ExercisePhrase.exercise_id == exercise.exercise_id
            )
        )
        phrase_ids = [row[0] for row in phrases_result.all()]

        is_overdue = (
            exercise.due_date is not None
            and exercise.due_date < now
            and assignment.completed_at is None
        )

        response.append(
            StudentExerciseResponse(
                exercise_id=exercise.exercise_id,
                class_id=exercise.class_id,
                title=exercise.title,
                due_date=exercise.due_date,
                assigned_at=assignment.assigned_at,
                completed_at=assignment.completed_at,
                is_overdue=is_overdue,
                phrase_ids=phrase_ids,
            )
        )

    return response


@router.get("/student/{student_uid}/assignments", response_model=list[StudentAssignmentResponse])
async def get_student_assignments(
    student_uid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await authorize_student_access(db, current_user, student_uid)

    assignments_result = await db.execute(
        select(ExerciseAssignment)
        .options(selectinload(ExerciseAssignment.exercise))
        .where(ExerciseAssignment.student_uid == student_uid)
        .order_by(ExerciseAssignment.assigned_at.desc())
    )
    assignments = assignments_result.scalars().all()
    now = datetime.now(timezone.utc)
    response: list[StudentAssignmentResponse] = []

    for assignment in assignments:
        exercise = assignment.exercise
        if exercise is None:
            continue

        phrase_ids = await _get_exercise_phrase_ids(db, exercise.exercise_id)
        submissions = await _get_student_phrase_submissions(
            db,
            exercise.exercise_id,
            student_uid,
        )
        submissions_by_phrase = {submission.phrase_id: submission for submission in submissions}

        response.append(
            StudentAssignmentResponse(
                exercise_id=exercise.exercise_id,
                class_id=exercise.class_id,
                title=exercise.title,
                due_date=exercise.due_date,
                assigned_at=assignment.assigned_at,
                completed_at=assignment.completed_at,
                is_overdue=(
                    exercise.due_date is not None
                    and exercise.due_date < now
                    and assignment.completed_at is None
                ),
                phrase_ids=phrase_ids,
                phrases=[
                    AssignmentPhraseStatus(
                        phrase_id=phrase_id,
                        submitted_at=submissions_by_phrase.get(phrase_id).submitted_at
                        if submissions_by_phrase.get(phrase_id)
                        else None,
                        reviewed_at=submissions_by_phrase.get(phrase_id).reviewed_at
                        if submissions_by_phrase.get(phrase_id)
                        else None,
                        released_at=submissions_by_phrase.get(phrase_id).released_at
                        if submissions_by_phrase.get(phrase_id)
                        else None,
                        teacher_accuracy_score=(
                            submissions_by_phrase.get(phrase_id).teacher_accuracy_score
                            if submissions_by_phrase.get(phrase_id)
                            and submissions_by_phrase.get(phrase_id).released_at is not None
                            else None
                        ),
                        teacher_feedback_text=(
                            submissions_by_phrase.get(phrase_id).teacher_feedback_text
                            if submissions_by_phrase.get(phrase_id)
                            and submissions_by_phrase.get(phrase_id).released_at is not None
                            else None
                        ),
                    )
                    for phrase_id in phrase_ids
                ],
            )
        )

    return response


@router.post("/{exercise_id}/submissions", response_model=AssignmentSubmissionResponse, status_code=201)
async def submit_assignment_phrase(
    exercise_id: str,
    phrase_id: str = Form(...),
    audio_file: UploadFile = File(...),
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):
    assignment = await _get_student_assignment(db, exercise_id, current_user.uid)
    phrase_ids = await _get_exercise_phrase_ids(db, exercise_id)

    if phrase_id not in phrase_ids:
        raise BadRequestException("Phrase is not part of this assignment")

    audio_bytes = await audio_file.read()
    try:
        validate_audio(audio_bytes, max_size_mb=settings.MAX_AUDIO_SIZE_MB)
    except ValueError as error:
        raise BadRequestException(str(error))

    phrase_result = await db.execute(select(Phrase).where(Phrase.phrase_id == phrase_id))
    phrase = phrase_result.scalar_one_or_none()
    if not phrase:
        raise NotFoundException(f"Phrase '{phrase_id}' not found")
    if not phrase.reference_audio_url:
        raise BadRequestException(
            f"Phrase '{phrase_id}' has no reference audio"
        )

    try:
        ref_object_key = get_object_key_from_url(phrase.reference_audio_url)
        reference_audio = download_audio(ref_object_key)
    except RuntimeError as error:
        raise BadRequestException(f"Could not fetch reference audio: {error}")

    phrase_candidates_result = await db.execute(
        select(Phrase.phrase_id, Phrase.japanese_text).where(
            Phrase.phrase_id.in_(phrase_ids)
        )
    )
    verification_candidate_rows = list(phrase_candidates_result.all())
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
    except Exception as error:
        raise BadRequestException(f"Verification failed: {error}")

    logger.info(
        "exercise submission verification student=%s exercise=%s phrase=%s status=%s recognized_phrase=%s confidence=%s margin=%s recognized_text=%s",
        current_user.uid,
        exercise_id,
        phrase.phrase_id,
        verification.status,
        verification.recognized_phrase_id,
        verification.verification_confidence,
        verification.verification_margin,
        verification.recognized_text,
    )

    pronunciation_target = build_reference_target_from_phrase(phrase)
    pronunciation_overrides = get_pronunciation_overrides(phrase)

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
    except Exception as error:
        raise BadRequestException(f"Scoring failed: {error}")

    logger.info(
        "exercise submission scoring student=%s exercise=%s phrase=%s verification_status=%s score=%.2f mora=%.2f consonant=%.2f vowel=%.2f counts_for_progress=%s",
        current_user.uid,
        exercise_id,
        phrase.phrase_id,
        verification.status,
        scores["accuracy_score"],
        scores["mora_timing_score"],
        scores["consonant_score"],
        scores["vowel_score"],
        verification.status == VERIFICATION_ACCEPTED,
    )

    existing_submission_result = await db.execute(
        select(ExerciseSubmission).where(
            ExerciseSubmission.exercise_id == exercise_id,
            ExerciseSubmission.student_uid == current_user.uid,
            ExerciseSubmission.phrase_id == phrase_id,
        )
    )
    submission = existing_submission_result.scalar_one_or_none()
    submission_id = submission.submission_id if submission else str(uuid.uuid4())
    object_key = f"assignment-audio/{exercise_id}/{current_user.uid}/{phrase_id}/{submission_id}.wav"

    try:
        audio_url = upload_audio(audio_bytes, object_key)
    except RuntimeError as error:
        raise BadRequestException(f"Audio upload failed: {error}")

    now = datetime.now(timezone.utc)
    if submission is None:
        submission = ExerciseSubmission(
            submission_id=submission_id,
            exercise_id=exercise_id,
            student_uid=current_user.uid,
            phrase_id=phrase_id,
            audio_file_url=audio_url,
            suggested_accuracy_score=scores["accuracy_score"],
            suggested_mora_timing_score=scores["mora_timing_score"],
            suggested_consonant_score=scores["consonant_score"],
            suggested_vowel_score=scores["vowel_score"],
            suggested_phoneme_error_map=scores["phoneme_error_map"],
            suggested_feedback_text=scores["feedback_text"],
            verification_status=verification.status,
            recognized_phrase_id=verification.recognized_phrase_id,
            recognized_text=verification.recognized_text,
            recognized_text_romaji=verification.recognized_text_romaji,
            target_pronunciation=scores["target_pronunciation"],
            pronunciation_feedback=scores["pronunciation_feedback"],
            verification_confidence=verification.verification_confidence,
            verification_margin=verification.verification_margin,
            counts_for_progress=verification.status == VERIFICATION_ACCEPTED,
            submitted_at=now,
        )
        db.add(submission)
    else:
        submission.audio_file_url = audio_url
        submission.suggested_accuracy_score = scores["accuracy_score"]
        submission.suggested_mora_timing_score = scores["mora_timing_score"]
        submission.suggested_consonant_score = scores["consonant_score"]
        submission.suggested_vowel_score = scores["vowel_score"]
        submission.suggested_phoneme_error_map = scores["phoneme_error_map"]
        submission.suggested_feedback_text = scores["feedback_text"]
        submission.verification_status = verification.status
        submission.recognized_phrase_id = verification.recognized_phrase_id
        submission.recognized_text = verification.recognized_text
        submission.recognized_text_romaji = verification.recognized_text_romaji
        submission.target_pronunciation = scores["target_pronunciation"]
        submission.pronunciation_feedback = scores["pronunciation_feedback"]
        submission.verification_confidence = verification.verification_confidence
        submission.verification_margin = verification.verification_margin
        submission.counts_for_progress = verification.status == VERIFICATION_ACCEPTED
        submission.teacher_accuracy_score = None
        submission.teacher_feedback_text = None
        submission.reviewed_at = None
        submission.released_at = None
        submission.submitted_at = now
        db.add(submission)

    await db.flush()
    await _sync_assignment_completion(db, assignment, phrase_ids)
    await db.commit()
    await db.refresh(submission)

    return submission


@router.get("/{exercise_id}/submissions", response_model=list[InstructorAssignmentSubmissionResponse])
async def get_exercise_submissions(
    exercise_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    exercise = await _get_owned_exercise(db, exercise_id, current_user.uid)

    result = await db.execute(
        select(ExerciseSubmission, User.display_name)
        .join(User, User.uid == ExerciseSubmission.student_uid)
        .where(ExerciseSubmission.exercise_id == exercise.exercise_id)
        .order_by(ExerciseSubmission.submitted_at.desc())
    )

    return [
        InstructorAssignmentSubmissionResponse(
            submission_id=submission.submission_id,
            exercise_id=submission.exercise_id,
            student_uid=submission.student_uid,
            student_display_name=student_display_name,
            phrase_id=submission.phrase_id,
            audio_file_url=submission.audio_file_url,
            submitted_at=submission.submitted_at,
            reviewed_at=submission.reviewed_at,
            released_at=submission.released_at,
            suggested_accuracy_score=submission.suggested_accuracy_score,
            suggested_mora_timing_score=submission.suggested_mora_timing_score,
            suggested_consonant_score=submission.suggested_consonant_score,
            suggested_vowel_score=submission.suggested_vowel_score,
            suggested_feedback_text=submission.suggested_feedback_text,
            verification_status=submission.verification_status,
            recognized_phrase_id=submission.recognized_phrase_id,
            recognized_text=submission.recognized_text,
            recognized_text_romaji=submission.recognized_text_romaji,
            target_pronunciation=submission.target_pronunciation,
            pronunciation_feedback=submission.pronunciation_feedback,
            verification_confidence=submission.verification_confidence,
            verification_margin=submission.verification_margin,
            counts_for_progress=submission.counts_for_progress,
            teacher_accuracy_score=submission.teacher_accuracy_score,
            teacher_feedback_text=submission.teacher_feedback_text,
        )
        for submission, student_display_name in result.all()
    ]


@router.patch("/submissions/{submission_id}/review", response_model=InstructorAssignmentSubmissionResponse)
async def review_assignment_submission(
    submission_id: str,
    body: ReviewAssignmentSubmissionRequest,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    submission = await _get_owned_submission(db, submission_id, current_user.uid)
    submission.teacher_accuracy_score = body.teacher_accuracy_score
    submission.teacher_feedback_text = body.teacher_feedback_text.strip()
    submission.reviewed_at = datetime.now(timezone.utc)
    submission.released_at = datetime.now(timezone.utc) if body.release_to_student else None
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    student_result = await db.execute(select(User.display_name).where(User.uid == submission.student_uid))
    student_display_name = student_result.scalar_one_or_none() or submission.student_uid

    return InstructorAssignmentSubmissionResponse(
        submission_id=submission.submission_id,
        exercise_id=submission.exercise_id,
        student_uid=submission.student_uid,
        student_display_name=student_display_name,
        phrase_id=submission.phrase_id,
        audio_file_url=submission.audio_file_url,
        submitted_at=submission.submitted_at,
        reviewed_at=submission.reviewed_at,
        released_at=submission.released_at,
        suggested_accuracy_score=submission.suggested_accuracy_score,
        suggested_mora_timing_score=submission.suggested_mora_timing_score,
        suggested_consonant_score=submission.suggested_consonant_score,
        suggested_vowel_score=submission.suggested_vowel_score,
        suggested_feedback_text=submission.suggested_feedback_text,
        verification_status=submission.verification_status,
        recognized_phrase_id=submission.recognized_phrase_id,
        recognized_text=submission.recognized_text,
        recognized_text_romaji=submission.recognized_text_romaji,
        target_pronunciation=submission.target_pronunciation,
        pronunciation_feedback=submission.pronunciation_feedback,
        verification_confidence=submission.verification_confidence,
        verification_margin=submission.verification_margin,
        counts_for_progress=submission.counts_for_progress,
        teacher_accuracy_score=submission.teacher_accuracy_score,
        teacher_feedback_text=submission.teacher_feedback_text,
    )


@router.post("/submissions/{submission_id}/release", response_model=InstructorAssignmentSubmissionResponse)
async def release_assignment_submission(
    submission_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    submission = await _get_owned_submission(db, submission_id, current_user.uid)
    if submission.reviewed_at is None:
        raise BadRequestException("Submission must be reviewed before release")

    submission.released_at = datetime.now(timezone.utc)
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    student_result = await db.execute(select(User.display_name).where(User.uid == submission.student_uid))
    student_display_name = student_result.scalar_one_or_none() or submission.student_uid

    return InstructorAssignmentSubmissionResponse(
        submission_id=submission.submission_id,
        exercise_id=submission.exercise_id,
        student_uid=submission.student_uid,
        student_display_name=student_display_name,
        phrase_id=submission.phrase_id,
        audio_file_url=submission.audio_file_url,
        submitted_at=submission.submitted_at,
        reviewed_at=submission.reviewed_at,
        released_at=submission.released_at,
        suggested_accuracy_score=submission.suggested_accuracy_score,
        suggested_mora_timing_score=submission.suggested_mora_timing_score,
        suggested_consonant_score=submission.suggested_consonant_score,
        suggested_vowel_score=submission.suggested_vowel_score,
        suggested_feedback_text=submission.suggested_feedback_text,
        verification_status=submission.verification_status,
        recognized_phrase_id=submission.recognized_phrase_id,
        recognized_text=submission.recognized_text,
        recognized_text_romaji=submission.recognized_text_romaji,
        target_pronunciation=submission.target_pronunciation,
        pronunciation_feedback=submission.pronunciation_feedback,
        verification_confidence=submission.verification_confidence,
        verification_margin=submission.verification_margin,
        counts_for_progress=submission.counts_for_progress,
        teacher_accuracy_score=submission.teacher_accuracy_score,
        teacher_feedback_text=submission.teacher_feedback_text,
    )


@router.patch("/{exercise_id}/complete", response_model=ExerciseAssignmentResponse)
async def mark_exercise_complete(
    exercise_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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
        return assignment

    assignment.completed_at = datetime.now(timezone.utc)
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    return assignment


@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    exercise = await _get_owned_exercise(db, exercise_id, current_user.uid)
    await db.delete(exercise)
    await db.commit()


async def _validate_phrase_ids(
    db: AsyncSession,
    phrase_ids: list[str],
):
    for phrase_id in phrase_ids:
        result = await db.execute(select(Phrase).where(Phrase.phrase_id == phrase_id))
        if result.scalar_one_or_none() is None:
            raise BadRequestException(f"Phrase '{phrase_id}' not found")


async def _validate_student_memberships(
    db: AsyncSession,
    class_id: str,
    student_uids: list[str],
):
    class_student_uids = set(await get_class_student_uids(db, class_id))
    missing_students = [student_uid for student_uid in student_uids if student_uid not in class_student_uids]
    if missing_students:
        raise BadRequestException(
            f"Students are not in this class: {', '.join(missing_students)}"
        )


async def _get_exercise(
    db: AsyncSession,
    exercise_id: str,
) -> Exercise:
    result = await db.execute(select(Exercise).where(Exercise.exercise_id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise NotFoundException(f"Exercise '{exercise_id}' not found")

    return exercise


async def _get_student_assignment(
    db: AsyncSession,
    exercise_id: str,
    student_uid: str,
) -> ExerciseAssignment:
    result = await db.execute(
        select(ExerciseAssignment).where(
            ExerciseAssignment.exercise_id == exercise_id,
            ExerciseAssignment.student_uid == student_uid,
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFoundException("Exercise assignment not found")

    return assignment


async def _get_exercise_phrase_ids(
    db: AsyncSession,
    exercise_id: str,
) -> list[str]:
    result = await db.execute(
        select(ExercisePhrase.phrase_id)
        .where(ExercisePhrase.exercise_id == exercise_id)
    )
    return [row[0] for row in result.all()]


async def _get_student_phrase_submissions(
    db: AsyncSession,
    exercise_id: str,
    student_uid: str,
) -> list[ExerciseSubmission]:
    result = await db.execute(
        select(ExerciseSubmission)
        .where(
            ExerciseSubmission.exercise_id == exercise_id,
            ExerciseSubmission.student_uid == student_uid,
        )
        .order_by(ExerciseSubmission.submitted_at.desc())
    )
    return result.scalars().all()


async def _sync_assignment_completion(
    db: AsyncSession,
    assignment: ExerciseAssignment,
    phrase_ids: list[str],
):
    result = await db.execute(
        select(ExerciseSubmission.phrase_id)
        .where(
            ExerciseSubmission.exercise_id == assignment.exercise_id,
            ExerciseSubmission.student_uid == assignment.student_uid,
        )
    )
    submitted_phrase_ids = {row[0] for row in result.all()}
    all_phrase_ids = set(phrase_ids)
    assignment.completed_at = (
        datetime.now(timezone.utc)
        if all_phrase_ids and all_phrase_ids.issubset(submitted_phrase_ids)
        else None
    )
    db.add(assignment)


async def _get_owned_submission(
    db: AsyncSession,
    submission_id: str,
    instructor_uid: str,
) -> ExerciseSubmission:
    result = await db.execute(
        select(ExerciseSubmission)
        .join(Exercise, Exercise.exercise_id == ExerciseSubmission.exercise_id)
        .where(
            ExerciseSubmission.submission_id == submission_id,
            Exercise.instructor_uid == instructor_uid,
        )
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise NotFoundException("Assignment submission not found")

    return submission


async def _get_owned_exercise(
    db: AsyncSession,
    exercise_id: str,
    instructor_uid: str,
    *,
    with_relationships: bool = False,
) -> Exercise:
    query = select(Exercise).where(Exercise.exercise_id == exercise_id)
    if with_relationships:
        query = query.options(
            selectinload(Exercise.phrases),
            selectinload(Exercise.assignments),
        )

    result = await db.execute(query)
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise NotFoundException(f"Exercise '{exercise_id}' not found")
    if exercise.instructor_uid != instructor_uid:
        raise ForbiddenException("You can only manage your own exercises")

    return exercise


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

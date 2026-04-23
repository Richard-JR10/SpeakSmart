from datetime import datetime
from typing import Literal

from pydantic import BaseModel

VerificationStatus = Literal[
    "accepted",
    "wrong_phrase_detected",
    "no_clear_speech",
    "retry_needed",
]


class AssignmentPhraseStatus(BaseModel):
    phrase_id: str
    submitted_at: datetime | None
    reviewed_at: datetime | None
    released_at: datetime | None
    teacher_accuracy_score: float | None
    teacher_feedback_text: str | None


class StudentAssignmentResponse(BaseModel):
    exercise_id: str
    class_id: str | None
    title: str
    due_date: datetime | None
    assigned_at: datetime
    completed_at: datetime | None
    is_overdue: bool
    phrase_ids: list[str]
    phrases: list[AssignmentPhraseStatus]


class AssignmentSubmissionResponse(BaseModel):
    submission_id: str
    exercise_id: str
    student_uid: str
    phrase_id: str
    audio_file_url: str
    submitted_at: datetime
    reviewed_at: datetime | None
    released_at: datetime | None
    verification_status: VerificationStatus
    recognized_phrase_id: str | None
    recognized_text: str | None
    recognized_text_romaji: str | None
    target_pronunciation: dict | None
    pronunciation_feedback: list[dict] | None
    verification_confidence: float | None
    verification_margin: float | None
    counts_for_progress: bool

    model_config = {"from_attributes": True}


class InstructorAssignmentSubmissionResponse(BaseModel):
    submission_id: str
    exercise_id: str
    student_uid: str
    student_display_name: str
    phrase_id: str
    audio_file_url: str
    submitted_at: datetime
    reviewed_at: datetime | None
    released_at: datetime | None
    suggested_accuracy_score: float
    suggested_mora_timing_score: float
    suggested_consonant_score: float
    suggested_vowel_score: float
    suggested_feedback_text: str | None
    verification_status: VerificationStatus
    recognized_phrase_id: str | None
    recognized_text: str | None
    recognized_text_romaji: str | None
    target_pronunciation: dict | None
    pronunciation_feedback: list[dict] | None
    verification_confidence: float | None
    verification_margin: float | None
    counts_for_progress: bool
    teacher_accuracy_score: float | None
    teacher_feedback_text: str | None


class ReviewAssignmentSubmissionRequest(BaseModel):
    teacher_accuracy_score: float
    teacher_feedback_text: str
    release_to_student: bool = False

from typing import Literal

from pydantic import BaseModel
from datetime import datetime

VerificationStatus = Literal[
    "accepted",
    "wrong_phrase_detected",
    "no_clear_speech",
    "retry_needed",
]


class AttemptResponse(BaseModel):
    attempt_id: str
    student_uid: str
    phrase_id: str
    audio_file_url: str | None
    accuracy_score: float
    mora_timing_score: float
    consonant_score: float
    vowel_score: float
    phoneme_error_map: dict | None
    feedback_text: str | None
    verification_status: VerificationStatus
    recognized_phrase_id: str | None
    recognized_text: str | None
    recognized_text_romaji: str | None
    target_pronunciation: dict | None
    pronunciation_feedback: list[dict] | None
    verification_confidence: float | None
    verification_margin: float | None
    counts_for_progress: bool
    attempted_at: datetime

    model_config = {"from_attributes": True}


class AttemptSummary(BaseModel):
    attempt_id: str
    phrase_id: str
    accuracy_score: float
    feedback_text: str | None
    verification_status: VerificationStatus
    recognized_phrase_id: str | None
    recognized_text: str | None
    recognized_text_romaji: str | None
    target_pronunciation: dict | None = None
    pronunciation_feedback: list[dict] | None = None
    counts_for_progress: bool
    attempted_at: datetime

    model_config = {"from_attributes": True}

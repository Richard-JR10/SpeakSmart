from pydantic import BaseModel
from datetime import datetime


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
    attempted_at: datetime

    model_config = {"from_attributes": True}


class AttemptSummary(BaseModel):
    attempt_id: str
    phrase_id: str
    accuracy_score: float
    feedback_text: str | None
    attempted_at: datetime

    model_config = {"from_attributes": True}
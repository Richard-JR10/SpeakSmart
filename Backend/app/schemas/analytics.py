from pydantic import BaseModel
from datetime import datetime

class StudentStat(BaseModel):
    uid: str
    display_name: str
    email: str
    overall_average: float
    total_attempts: int
    streak_days: int
    weakest_module_id: str | None
    is_flagged: bool

    model_config = {
        "from_attributes": True
    }

class PhonemeErrorBreakdown(BaseModel):
    mora_timing_avg: float
    consonant_avg: float
    vowel_avg: float
    overall_avg: float

class WeeklyClassAccuracy(BaseModel):
    week_start: str
    average_accuracy: float
    attempt_count: int
    active_students: int

class ClassOverview(BaseModel):
    class_id: str
    total_students: int
    active_students: int
    weekly_attempts: int
    class_average: float
    flagged_students: list[StudentStat]
    phoneme_breakdown: PhonemeErrorBreakdown
    weekly_trend: list[WeeklyClassAccuracy]

class StudentDrillDown(BaseModel):
    uid: str
    display_name: str
    email: str
    overall_average: float
    total_attempts: int
    streak_days: int
    phoneme_breakdown: PhonemeErrorBreakdown
    weakest_module_id: str | None
    weakest_module_score: float | None
    recent_attempts: list[dict]
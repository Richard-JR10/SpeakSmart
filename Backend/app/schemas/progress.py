from pydantic import BaseModel
from datetime import datetime

class ProgressSummaryResponse(BaseModel):
    id: int
    student_uid: str
    module_id: str
    average_accuracy: float
    total_attempts: int
    streak_days: int
    last_attempted_at: datetime | None
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class WeeklyAccuracy(BaseModel):
    week_start: str # ISO date string e.g. "2026-04-07"
    average_accuracy: float
    attempt_count: int

class StudentDashboard(BaseModel):
    overall_average: float
    total_attempts: int
    streak_days: int
    weakest_module_id: str | None
    weakest_module_score: float | None
    progress_by_module: list[ProgressSummaryResponse]
    weekly_accuracy: list[WeeklyAccuracy]
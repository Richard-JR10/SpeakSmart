# app/schemas/exercise.py
from pydantic import BaseModel
from datetime import datetime


class ExerciseCreateRequest(BaseModel):
    exercise_id: str
    class_id: str
    title: str
    phrase_ids: list[str]
    student_uids: list[str]
    due_date: datetime | None = None


class ExercisePhraseResponse(BaseModel):
    id: int
    exercise_id: str
    phrase_id: str

    model_config = {"from_attributes": True}


class ExerciseAssignmentResponse(BaseModel):
    id: int
    exercise_id: str
    student_uid: str
    assigned_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ExerciseResponse(BaseModel):
    exercise_id: str
    title: str
    instructor_uid: str
    class_id: str | None
    created_at: datetime
    due_date: datetime | None
    phrases: list[ExercisePhraseResponse]
    assignments: list[ExerciseAssignmentResponse]

    model_config = {"from_attributes": True}


class StudentExerciseResponse(BaseModel):
    exercise_id: str
    class_id: str | None
    title: str
    due_date: datetime | None
    assigned_at: datetime
    completed_at: datetime | None
    is_overdue: bool
    phrase_ids: list[str]

    model_config = {"from_attributes": True}

from datetime import datetime

from pydantic import BaseModel, Field


class ClassCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class JoinClassRequest(BaseModel):
    join_code: str = Field(min_length=4, max_length=32)


class ClassSummaryResponse(BaseModel):
    class_id: str
    name: str
    instructor_uid: str
    instructor_name: str | None
    join_code: str | None
    created_at: datetime
    joined_at: datetime | None
    student_count: int
    is_owner: bool


class JoinCodeResponse(BaseModel):
    class_id: str
    join_code: str

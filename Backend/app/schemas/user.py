import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from datetime import datetime


_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: str
    role: str
    created_at: datetime
    last_login: datetime | None

    model_config = {
        "from_attributes": True
    }


class UserUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("display_name")
    @classmethod
    def sanitize_display_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if _CONTROL_CHAR_RE.search(v):
            raise ValueError("Display name contains invalid characters")
        return v or None


class UserRegisterRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    role: Literal["student", "instructor"]

    @field_validator("display_name")
    @classmethod
    def sanitize_display_name(cls, v: str) -> str:
        v = v.strip()
        if _CONTROL_CHAR_RE.search(v):
            raise ValueError("Display name contains invalid characters")
        if not v:
            raise ValueError("Display name cannot be blank")
        return v

from typing import Literal

from pydantic import BaseModel, Field
from datetime import datetime

class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: str
    role: str
    class_id: str | None
    created_at: datetime
    last_login: datetime | None
    
    model_config = {
        "from_attributes": True
    }

class UserUpdateRequest(BaseModel):
    display_name: str | None = None
    class_id: str | None = None


class UserRegisterRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=255)
    role: Literal["student", "instructor"]

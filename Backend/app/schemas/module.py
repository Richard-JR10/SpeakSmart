from pydantic import BaseModel
from datetime import datetime

class ModuleBase(BaseModel):
    module_id: str
    title: str
    description: str | None
    order_index: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

class ModuleCreateRequest(BaseModel):
    module_id: str
    title: str
    description: str | None
    order_index: int = 0
from pydantic import BaseModel
from datetime import datetime

class PhraseResponse(BaseModel):
    phrase_id: str
    module_id: str
    japanese_text: str
    romaji: str
    english_translation: str
    reference_audio_url: str | None
    difficulty_level: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class PhraseCreateRequest(BaseModel):
    phrase_id: str
    module_id: str
    japanese_text: str
    romaji: str
    english_translation: str
    reference_audio_url: str | None = None
    difficulty_level: int = 1
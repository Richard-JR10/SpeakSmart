from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_current_user, require_instructor, get_db
from app.db.models.user import User
from app.db.models.phrase import Phrase
from app.schemas.phrase import PhraseResponse, PhraseCreateRequest
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/phrases", tags=["phrases"])


@router.get("/{phrase_id}", response_model=PhraseResponse)
async def get_phrase(
    phrase_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns a single phrase by ID."""
    result = await db.execute(
        select(Phrase).where(Phrase.phrase_id == phrase_id)
    )
    phrase = result.scalar_one_or_none()
    if not phrase:
        raise NotFoundException(f"Phrase '{phrase_id}' not found")
    return phrase


@router.post("", response_model=PhraseResponse, status_code=201)
async def create_phrase(
    body: PhraseCreateRequest,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Instructor only — creates a new phrase."""
    phrase = Phrase(
        phrase_id=body.phrase_id,
        module_id=body.module_id,
        japanese_text=body.japanese_text,
        romaji=body.romaji,
        english_translation=body.english_translation,
        reference_audio_url=body.reference_audio_url,
        difficulty_level=body.difficulty_level,
    )
    db.add(phrase)
    await db.commit()
    await db.refresh(phrase)
    return phrase


@router.delete("/{phrase_id}", status_code=204)
async def delete_phrase(
    phrase_id: str,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Instructor only — deletes a phrase."""
    result = await db.execute(
        select(Phrase).where(Phrase.phrase_id == phrase_id)
    )
    phrase = result.scalar_one_or_none()
    if not phrase:
        raise NotFoundException(f"Phrase '{phrase_id}' not found")
    await db.delete(phrase)
    await db.commit()
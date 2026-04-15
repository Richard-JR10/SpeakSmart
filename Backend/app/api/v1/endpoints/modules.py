# app/api/v1/endpoints/modules.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_current_user, require_instructor, get_db
from app.db.models.user import User
from app.db.models.module import Module
from app.db.models.phrase import Phrase
from app.schemas.module import ModuleResponse, ModuleCreateRequest
from app.schemas.phrase import PhraseResponse
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("", response_model=list[ModuleResponse])
async def list_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all lesson modules ordered by index."""
    result = await db.execute(
        select(Module).order_by(Module.order_index)
    )
    return result.scalars().all()


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns a single module by ID."""
    result = await db.execute(
        select(Module).where(Module.module_id == module_id)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise NotFoundException(f"Module '{module_id}' not found")
    return module


@router.get("/{module_id}/phrases", response_model=list[PhraseResponse])
async def list_phrases_for_module(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all phrases belonging to a module, ordered by difficulty."""
    # Verify module exists first
    mod_result = await db.execute(
        select(Module).where(Module.module_id == module_id)
    )
    if not mod_result.scalar_one_or_none():
        raise NotFoundException(f"Module '{module_id}' not found")

    result = await db.execute(
        select(Phrase)
        .where(Phrase.module_id == module_id)
        .order_by(Phrase.difficulty_level)
    )
    return result.scalars().all()


@router.post("", response_model=ModuleResponse, status_code=201)
async def create_module(
    body: ModuleCreateRequest,
    current_user: User = Depends(require_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Instructor only — creates a new lesson module."""
    module = Module(
        module_id=body.module_id,
        title=body.title,
        description=body.description,
        order_index=body.order_index,
    )
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module
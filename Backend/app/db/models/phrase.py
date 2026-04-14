# app/db/models/phrase.py
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Phrase(Base):
    __tablename__ = "phrases"

    phrase_id: Mapped[str] = mapped_column(String, primary_key=True)
    module_id: Mapped[str] = mapped_column(String, ForeignKey("modules.module_id"), nullable=False)
    japanese_text: Mapped[str] = mapped_column(String, nullable=False)
    romaji: Mapped[str] = mapped_column(String, nullable=False)
    english_translation: Mapped[str] = mapped_column(String, nullable=False)
    reference_audio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    module: Mapped["Module"] = relationship("Module", back_populates="phrases")
    attempts: Mapped[list["Attempt"]] = relationship("Attempt", back_populates="phrase")
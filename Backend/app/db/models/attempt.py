# app/db/models/attempt.py
from sqlalchemy import String, Float, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Attempt(Base):
    __tablename__ = "attempts"

    attempt_id: Mapped[str] = mapped_column(String, primary_key=True)
    student_uid: Mapped[str] = mapped_column(String, ForeignKey("users.uid"), nullable=False)
    phrase_id: Mapped[str] = mapped_column(String, ForeignKey("phrases.phrase_id"), nullable=False)
    audio_file_url: Mapped[str | None] = mapped_column(String, nullable=True)
    accuracy_score: Mapped[float] = mapped_column(Float, nullable=False)
    mora_timing_score: Mapped[float] = mapped_column(Float, nullable=False)
    consonant_score: Mapped[float] = mapped_column(Float, nullable=False)
    vowel_score: Mapped[float] = mapped_column(Float, nullable=False)
    phoneme_error_map: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    feedback_text: Mapped[str | None] = mapped_column(String, nullable=True)
    attempted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["User"] = relationship("User", back_populates="attempts")
    phrase: Mapped["Phrase"] = relationship("Phrase", back_populates="attempts")
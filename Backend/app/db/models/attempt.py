# app/db/models/attempt.py
from sqlalchemy import Boolean, String, Float, JSON, ForeignKey, DateTime, func
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
    verification_status: Mapped[str] = mapped_column(String, nullable=False, default="accepted")
    recognized_phrase_id: Mapped[str | None] = mapped_column(String, nullable=True)
    recognized_text: Mapped[str | None] = mapped_column(String, nullable=True)
    recognized_text_romaji: Mapped[str | None] = mapped_column(String, nullable=True)
    target_pronunciation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    pronunciation_feedback: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    verification_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    verification_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    counts_for_progress: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    attempted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["User"] = relationship("User", back_populates="attempts")
    phrase: Mapped["Phrase"] = relationship("Phrase", back_populates="attempts")

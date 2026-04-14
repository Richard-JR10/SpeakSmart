# app/db/models/progress.py
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ProgressSummary(Base):
    __tablename__ = "progress_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_uid: Mapped[str] = mapped_column(String, ForeignKey("users.uid"), nullable=False)
    module_id: Mapped[str] = mapped_column(String, ForeignKey("modules.module_id"), nullable=False)
    average_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_attempted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student: Mapped["User"] = relationship("User", back_populates="progress_summaries")
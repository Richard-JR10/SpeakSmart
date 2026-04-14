# app/db/models/analytics.py
from sqlalchemy import String, Float, Integer, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ClassAnalytics(Base):
    __tablename__ = "class_analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[str] = mapped_column(String, nullable=False)
    week_start: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    average_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    active_students: Mapped[int] = mapped_column(Integer, default=0)
    phoneme_error_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    computed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
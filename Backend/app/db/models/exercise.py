# app/db/models/exercise.py
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    exercise_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    instructor_uid: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    due_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    phrases: Mapped[list["ExercisePhrase"]] = relationship(
        "ExercisePhrase", 
        back_populates="exercise",
        cascade="all, delete-orphan"
    )
    assignments: Mapped[list["ExerciseAssignment"]] = relationship(
        "ExerciseAssignment", 
        back_populates="exercise",
        cascade="all, delete-orphan"
    )


class ExercisePhrase(Base):
    __tablename__ = "exercise_phrases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exercise_id: Mapped[str] = mapped_column(String, ForeignKey("exercises.exercise_id"), nullable=False)
    phrase_id: Mapped[str] = mapped_column(String, ForeignKey("phrases.phrase_id"), nullable=False)

    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="phrases")


class ExerciseAssignment(Base):
    __tablename__ = "exercise_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exercise_id: Mapped[str] = mapped_column(String, ForeignKey("exercises.exercise_id"), nullable=False)
    student_uid: Mapped[str] = mapped_column(String, ForeignKey("users.uid"), nullable=False)
    assigned_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="assignments")
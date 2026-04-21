# app/db/models/exercise.py
from sqlalchemy import String, Integer, Float, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    exercise_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    instructor_uid: Mapped[str] = mapped_column(String, nullable=False)
    class_id: Mapped[str | None] = mapped_column(String, ForeignKey("classes.class_id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    due_date: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    class_: Mapped["Class"] = relationship("Class", back_populates="exercises")
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
    submissions: Mapped[list["ExerciseSubmission"]] = relationship(
        "ExerciseSubmission",
        back_populates="exercise",
        cascade="all, delete-orphan",
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


class ExerciseSubmission(Base):
    __tablename__ = "exercise_submissions"

    submission_id: Mapped[str] = mapped_column(String, primary_key=True)
    exercise_id: Mapped[str] = mapped_column(String, ForeignKey("exercises.exercise_id"), nullable=False)
    student_uid: Mapped[str] = mapped_column(String, ForeignKey("users.uid"), nullable=False)
    phrase_id: Mapped[str] = mapped_column(String, ForeignKey("phrases.phrase_id"), nullable=False)
    audio_file_url: Mapped[str] = mapped_column(String, nullable=False)
    suggested_accuracy_score: Mapped[float] = mapped_column(Float, nullable=False)
    suggested_mora_timing_score: Mapped[float] = mapped_column(Float, nullable=False)
    suggested_consonant_score: Mapped[float] = mapped_column(Float, nullable=False)
    suggested_vowel_score: Mapped[float] = mapped_column(Float, nullable=False)
    suggested_phoneme_error_map: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    suggested_feedback_text: Mapped[str | None] = mapped_column(String, nullable=True)
    teacher_accuracy_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    teacher_feedback_text: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    released_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="submissions")

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Class(Base):
    __tablename__ = "classes"

    class_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    instructor_uid: Mapped[str] = mapped_column(String, nullable=False)
    join_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    memberships: Mapped[list["ClassMembership"]] = relationship(
        "ClassMembership",
        back_populates="class_",
        cascade="all, delete-orphan",
    )
    exercises: Mapped[list["Exercise"]] = relationship(
        "Exercise",
        back_populates="class_",
    )


class ClassMembership(Base):
    __tablename__ = "class_memberships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    class_id: Mapped[str] = mapped_column(String, ForeignKey("classes.class_id"), nullable=False)
    user_uid: Mapped[str] = mapped_column(String, ForeignKey("users.uid"), nullable=False)
    joined_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    class_: Mapped["Class"] = relationship("Class", back_populates="memberships")
    user: Mapped["User"] = relationship("User", back_populates="class_memberships")

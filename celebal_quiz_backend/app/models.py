"""SQLAlchemy database models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Question(Base):
    """A quiz question with one or more answer choices."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question_text: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="python", nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), default="intermediate", nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    choices: Mapped[list[Choice]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Choice.id",
    )

    __table_args__ = (
        Index("ix_questions_category_difficulty", "category", "difficulty"),
    )


class Choice(Base):
    """An answer option belonging to a question."""

    __tablename__ = "choices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    choice_text: Mapped[str] = mapped_column(String(300), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    question: Mapped[Question] = relationship(back_populates="choices")

    __table_args__ = (
        Index("ix_choices_question_text", "question_id", "choice_text", unique=True),
    )

"""Reusable database operations for questions and choices."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas


def get_question(db: Session, question_id: int) -> models.Question | None:
    statement = (
        select(models.Question)
        .options(selectinload(models.Question.choices))
        .where(models.Question.id == question_id)
    )
    return db.scalar(statement)


def list_questions(
    db: Session,
    *,
    category: str | schemas.QuizCategory | None = None,
    difficulty: schemas.Difficulty | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Question]:
    statement = select(models.Question).options(selectinload(models.Question.choices))

    if category:
        category_val = category.value if hasattr(category, "value") else category
        statement = statement.where(func.lower(models.Question.category) == category_val.lower())
    if difficulty:
        statement = statement.where(models.Question.difficulty == difficulty.value)
    if search:
        statement = statement.where(models.Question.question_text.ilike(f"%{search}%"))

    statement = statement.order_by(models.Question.id).offset(skip).limit(limit)
    return list(db.scalars(statement).unique().all())


def create_question(db: Session, payload: schemas.QuestionCreate) -> models.Question:
    question = models.Question(
        question_text=payload.question_text.strip(),
        category=payload.category.value,
        difficulty=payload.difficulty.value,
        explanation=payload.explanation.strip() if payload.explanation else None,
    )
    question.choices = [
        models.Choice(
            choice_text=choice.choice_text.strip(), is_correct=choice.is_correct
        )
        for choice in payload.choices
    ]
    db.add(question)
    db.commit()
    db.refresh(question)
    return get_question(db, question.id) or question


def update_question(
    db: Session, question: models.Question, payload: schemas.QuestionUpdate
) -> models.Question:
    updates = payload.model_dump(exclude_unset=True)
    if "difficulty" in updates and updates["difficulty"] is not None:
        updates["difficulty"] = updates["difficulty"].value
    if "category" in updates and updates["category"] is not None:
        updates["category"] = updates["category"].value
    for text_field in ("question_text", "explanation"):
        if text_field in updates and isinstance(updates[text_field], str):
            updates[text_field] = updates[text_field].strip()
    for field, value in updates.items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return get_question(db, question.id) or question


def delete_question(db: Session, question: models.Question) -> None:
    db.delete(question)
    db.commit()


def get_choice(db: Session, choice_id: int) -> models.Choice | None:
    return db.get(models.Choice, choice_id)


def list_choices(
    db: Session, question_id: int | None = None, skip: int = 0, limit: int = 200
) -> list[models.Choice]:
    statement = select(models.Choice)
    if question_id is not None:
        statement = statement.where(models.Choice.question_id == question_id)
    statement = statement.order_by(models.Choice.id).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def create_choice(db: Session, payload: schemas.ChoiceCreate) -> models.Choice:
    choice = models.Choice(
        question_id=payload.question_id,
        choice_text=payload.choice_text.strip(),
        is_correct=payload.is_correct,
    )
    db.add(choice)
    db.commit()
    db.refresh(choice)
    return choice


def update_choice(
    db: Session, choice: models.Choice, payload: schemas.ChoiceUpdate
) -> models.Choice:
    updates = payload.model_dump(exclude_unset=True)
    if "choice_text" in updates and updates["choice_text"] is not None:
        updates["choice_text"] = updates["choice_text"].strip()
    for field, value in updates.items():
        setattr(choice, field, value)
    db.commit()
    db.refresh(choice)
    return choice


def delete_choice(db: Session, choice: models.Choice) -> None:
    db.delete(choice)
    db.commit()

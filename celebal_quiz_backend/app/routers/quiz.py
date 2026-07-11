"""Quiz-taking and scoring endpoints."""

from __future__ import annotations

import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.get("/start", response_model=list[schemas.QuizQuestion])
def start_quiz(
    category: schemas.QuizCategory | None = None,
    difficulty: schemas.Difficulty | None = None,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[schemas.QuizQuestion]:
    statement = select(models.Question).options(selectinload(models.Question.choices))
    if category:
        statement = statement.where(func.lower(models.Question.category) == category.value.lower())
    if difficulty:
        statement = statement.where(models.Question.difficulty == difficulty.value)

    questions = list(db.scalars(statement).unique().all())
    ready_questions = [
        question
        for question in questions
        if len(question.choices) >= 2
        and sum(choice.is_correct for choice in question.choices) == 1
    ]

    if not ready_questions:
        raise HTTPException(
            status_code=404,
            detail="No quiz-ready questions match the selected filters.",
        )

    selected = random.sample(ready_questions, min(limit, len(ready_questions)))
    return [
        schemas.QuizQuestion(
            id=question.id,
            question_text=question.question_text,
            category=question.category,
            difficulty=question.difficulty,
            choices=[
                schemas.PublicChoice(id=choice.id, choice_text=choice.choice_text)
                for choice in question.choices
            ],
        )
        for question in selected
    ]


@router.post("/submit", response_model=schemas.QuizResult)
def submit_quiz(
    payload: schemas.QuizSubmission, db: Session = Depends(get_db)
) -> schemas.QuizResult:
    results: list[schemas.AnswerResult] = []

    for answer in payload.answers:
        statement = (
            select(models.Question)
            .options(selectinload(models.Question.choices))
            .where(models.Question.id == answer.question_id)
        )
        question = db.scalar(statement)
        if question is None:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID {answer.question_id} was not found.",
            )

        selected_choice = next(
            (choice for choice in question.choices if choice.id == answer.choice_id),
            None,
        )
        if selected_choice is None:
            raise HTTPException(
                status_code=400,
                detail="The selected choice does not belong to this question.",
            )

        correct_choices = [choice for choice in question.choices if choice.is_correct]
        if len(correct_choices) != 1:
            raise HTTPException(
                status_code=409,
                detail=f"Question {answer.question_id} is not configured correctly.",
            )
        correct_choice = correct_choices[0]
        results.append(
            schemas.AnswerResult(
                question_id=question.id,
                selected_choice_id=selected_choice.id,
                correct_choice_id=correct_choice.id,
                is_correct=selected_choice.id == correct_choice.id,
                explanation=question.explanation,
            )
        )

    correct_answers = sum(result.is_correct for result in results)
    total = len(results)
    percentage = round((correct_answers / total) * 100, 2)
    return schemas.QuizResult(
        total_questions=total,
        correct_answers=correct_answers,
        wrong_answers=total - correct_answers,
        percentage=percentage,
        results=results,
    )

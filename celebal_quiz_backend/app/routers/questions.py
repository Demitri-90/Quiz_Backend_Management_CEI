"""Question management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("", response_model=schemas.QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(
    payload: schemas.QuestionCreate, db: Session = Depends(get_db)
) -> models.Question:
    try:
        return crud.create_question(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A question with the same text already exists.",
        ) from exc


@router.get("", response_model=list[schemas.QuestionRead])
def get_all_questions(
    category: schemas.QuizCategory | None = None,
    difficulty: schemas.Difficulty | None = None,
    search: str | None = Query(default=None, min_length=1, max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[models.Question]:
    return crud.list_questions(
        db,
        category=category,
        difficulty=difficulty,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get("/categories", response_model=list[str])
def get_categories(db: Session = Depends(get_db)) -> list[str]:
    statement = select(models.Question.category).distinct().order_by(func.lower(models.Question.category))
    return list(db.scalars(statement).all())


@router.get("/{question_id}", response_model=schemas.QuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db)) -> models.Question:
    question = crud.get_question(db, question_id)
    if question is None:
        raise HTTPException(
            status_code=404,
            detail=f"Question with ID {question_id} was not found.",
        )
    return question


@router.put("/{question_id}", response_model=schemas.QuestionRead)
@router.patch("/{question_id}", response_model=schemas.QuestionRead, include_in_schema=False)
def update_question(
    question_id: int,
    payload: schemas.QuestionUpdate,
    db: Session = Depends(get_db),
) -> models.Question:
    question = crud.get_question(db, question_id)
    if question is None:
        raise HTTPException(
            status_code=404,
            detail=f"Question with ID {question_id} was not found.",
        )
    try:
        return crud.update_question(db, question, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A question with the same text already exists.",
        ) from exc


@router.delete("/{question_id}", response_model=schemas.MessageResponse)
def delete_question(
    question_id: int, db: Session = Depends(get_db)
) -> schemas.MessageResponse:
    question = crud.get_question(db, question_id)
    if question is None:
        raise HTTPException(
            status_code=404,
            detail=f"Question with ID {question_id} was not found.",
        )
    crud.delete_question(db, question)
    return schemas.MessageResponse(
        message=f"Question {question_id} and its choices were deleted successfully."
    )

"""Choice management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/choices", tags=["Choices"])


def ensure_correct_choice_is_unique(
    db: Session,
    *,
    question_id: int,
    is_correct: bool,
    exclude_choice_id: int | None = None,
) -> None:
    if not is_correct:
        return
    statement = select(models.Choice).where(
        models.Choice.question_id == question_id,
        models.Choice.is_correct.is_(True),
    )
    if exclude_choice_id is not None:
        statement = statement.where(models.Choice.id != exclude_choice_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=400,
            detail="This question already has a correct choice.",
        )


@router.post("", response_model=schemas.ChoiceRead, status_code=status.HTTP_201_CREATED)
def create_choice(
    payload: schemas.ChoiceCreate, db: Session = Depends(get_db)
) -> models.Choice:
    question = crud.get_question(db, payload.question_id)
    if question is None:
        raise HTTPException(
            status_code=404,
            detail=f"Question with ID {payload.question_id} was not found.",
        )
    ensure_correct_choice_is_unique(
        db, question_id=payload.question_id, is_correct=payload.is_correct
    )
    try:
        return crud.create_choice(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This choice already exists for the selected question.",
        ) from exc


@router.get("", response_model=list[schemas.ChoiceRead])
def get_all_choices(
    question_id: int | None = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[models.Choice]:
    return crud.list_choices(db, question_id=question_id, skip=skip, limit=limit)


@router.get("/{choice_id}", response_model=schemas.ChoiceRead)
def get_choice(choice_id: int, db: Session = Depends(get_db)) -> models.Choice:
    choice = crud.get_choice(db, choice_id)
    if choice is None:
        raise HTTPException(status_code=404, detail="Choice not found.")
    return choice


@router.put("/{choice_id}", response_model=schemas.ChoiceRead)
@router.patch("/{choice_id}", response_model=schemas.ChoiceRead, include_in_schema=False)
def update_choice(
    choice_id: int,
    payload: schemas.ChoiceUpdate,
    db: Session = Depends(get_db),
) -> models.Choice:
    choice = crud.get_choice(db, choice_id)
    if choice is None:
        raise HTTPException(status_code=404, detail="Choice not found.")

    target_is_correct = (
        payload.is_correct if payload.is_correct is not None else choice.is_correct
    )
    ensure_correct_choice_is_unique(
        db,
        question_id=choice.question_id,
        is_correct=target_is_correct,
        exclude_choice_id=choice.id,
    )
    try:
        return crud.update_choice(db, choice, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This choice already exists for the selected question.",
        ) from exc


@router.delete("/{choice_id}", response_model=schemas.MessageResponse)
def delete_choice(
    choice_id: int, db: Session = Depends(get_db)
) -> schemas.MessageResponse:
    choice = crud.get_choice(db, choice_id)
    if choice is None:
        raise HTTPException(status_code=404, detail="Choice not found.")
    crud.delete_choice(db, choice)
    return schemas.MessageResponse(message=f"Choice {choice_id} deleted successfully.")

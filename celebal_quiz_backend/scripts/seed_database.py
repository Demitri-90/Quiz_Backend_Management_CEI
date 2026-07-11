"""Seed the database with questions from data/quiz_questions.json."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path to allow absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Choice, Question
from app import schemas


def seed_database() -> None:
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)

    json_path = Path(__file__).resolve().parent.parent / "data" / "quiz_questions.json"
    if not json_path.exists():
        print(f"Error: Dataset file not found at {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            raw_questions = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"Error decoding JSON: {exc}")
            sys.exit(1)

    inserted_count = 0
    skipped_count = 0
    invalid_count = 0

    print("Starting dataset validation...")

    with SessionLocal() as db:
        for index, item in enumerate(raw_questions):
            # 1. Map fields from JSON structure to Pydantic schemas
            try:
                mapped_choices = []
                for choice_item in item.get("choices", []):
                    mapped_choices.append({
                        "choice_text": choice_item.get("text"),
                        "is_correct": choice_item.get("is_correct", False),
                    })

                mapped_question = {
                    "question_text": item.get("text"),
                    "category": item.get("category"),
                    "difficulty": item.get("difficulty"),
                    "explanation": item.get("explanation"),
                    "choices": mapped_choices,
                }

                # 2. Validate using Pydantic schema
                validated_question = schemas.QuestionCreate(**mapped_question)
            except ValidationError as exc:
                invalid_count += 1
                question_text_preview = item.get("text", f"Question at index {index}")
                print(f"Invalid record: '{question_text_preview}'")
                print(f"  Reason: {exc.errors()[0]['msg']}")
                continue
            except Exception as exc:
                invalid_count += 1
                question_text_preview = item.get("text", f"Question at index {index}")
                print(f"Invalid record: '{question_text_preview}'")
                print(f"  Reason: {str(exc)}")
                continue

            # 3. Check for duplicates in the DB (Idempotency)
            statement = select(Question).where(Question.question_text == validated_question.question_text.strip())
            existing_question = db.scalar(statement)
            if existing_question is not None:
                skipped_count += 1
                continue

            # 4. Insert question and choices using a transaction
            try:
                question_db = Question(
                    question_text=validated_question.question_text.strip(),
                    category=validated_question.category.value,
                    difficulty=validated_question.difficulty.value,
                    explanation=validated_question.explanation.strip() if validated_question.explanation else None,
                )
                question_db.choices = [
                    Choice(
                        choice_text=choice.choice_text.strip(),
                        is_correct=choice.is_correct
                    )
                    for choice in validated_question.choices
                ]
                db.add(question_db)
                db.commit()
                inserted_count += 1
            except Exception as exc:
                db.rollback()
                print(f"Database error while inserting '{validated_question.question_text}': {exc}")
                sys.exit(1)

    print("\nDataset validation completed.")
    print(f"Questions inserted: {inserted_count}")
    print(f"Questions skipped: {skipped_count}")
    print(f"Invalid questions: {invalid_count}")


if __name__ == "__main__":
    seed_database()

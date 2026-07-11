"""Tests for quiz-taking flow, scoring logic, and database seeding."""

from __future__ import annotations

from fastapi.testclient import TestClient
from scripts.seed_database import seed_database
from app.database import SessionLocal
from app.models import Question, Choice


def test_quiz_flow(client: TestClient) -> None:
    # 1. Create a question
    create_response = client.post(
        "/questions",
        json={
            "question_text": "Which HTTP method retrieves a resource without changing it?",
            "category": "fastapi",
            "difficulty": "beginner",
            "explanation": "GET is used for retrieval.",
            "choices": [
                {"choice_text": "GET", "is_correct": True},
                {"choice_text": "POST", "is_correct": False},
            ],
        },
    )
    assert create_response.status_code == 201
    question = create_response.json()
    correct_choice_id = next(
        choice["id"] for choice in question["choices"] if choice["is_correct"]
    )
    wrong_choice_id = next(
        choice["id"] for choice in question["choices"] if not choice["is_correct"]
    )

    # 2. Start quiz - Category query is lowercase
    start_response = client.get("/quiz/start?category=fastapi&limit=1")
    assert start_response.status_code == 200
    quiz_question = start_response.json()[0]
    # Check that privacy is preserved (is_correct must not appear when starting a quiz)
    assert "is_correct" not in quiz_question["choices"][0]

    # 3. Submit quiz with correct answer
    submit_response = client.post(
        "/quiz/submit",
        json={
            "answers": [
                {"question_id": question["id"], "choice_id": correct_choice_id}
            ]
        },
    )
    assert submit_response.status_code == 200
    result = submit_response.json()
    assert result["correct_answers"] == 1
    assert result["percentage"] == 100.0
    assert result["results"][0]["is_correct"] is True
    assert result["results"][0]["explanation"] == "GET is used for retrieval."

    # 4. Submit quiz with incorrect answer
    submit_wrong = client.post(
        "/quiz/submit",
        json={
            "answers": [
                {"question_id": question["id"], "choice_id": wrong_choice_id}
            ]
        },
    )
    assert submit_wrong.status_code == 200
    assert submit_wrong.json()["correct_answers"] == 0
    assert submit_wrong.json()["percentage"] == 0.0

    # 5. Submit quiz with invalid choice belonging to a different question
    # Create another question
    other_response = client.post(
        "/questions",
        json={
            "question_text": "What is Python?",
            "category": "python",
            "difficulty": "beginner",
            "choices": [
                {"choice_text": "Language", "is_correct": True},
                {"choice_text": "Snake", "is_correct": False},
            ],
        },
    )
    other_choice_id = other_response.json()["choices"][0]["id"]
    submit_invalid_choice = client.post(
        "/quiz/submit",
        json={
            "answers": [
                {"question_id": question["id"], "choice_id": other_choice_id}
            ]
        },
    )
    assert submit_invalid_choice.status_code == 400
    assert submit_invalid_choice.json()["detail"] == "The selected choice does not belong to this question."


def test_skipped_answers(client: TestClient) -> None:
    # Submit with no answers (empty list) -> should fail schema validation with 422
    response = client.post("/quiz/submit", json={"answers": []})
    assert response.status_code == 422


def test_seeding_script_idempotency() -> None:
    # 1. Run seed database once
    seed_database()
    with SessionLocal() as db:
        initial_count = db.query(Question).count()
        assert initial_count >= 30

    # 2. Run seed database again (idempotent, shouldn't add duplicates)
    seed_database()
    with SessionLocal() as db:
        second_count = db.query(Question).count()
        assert initial_count == second_count

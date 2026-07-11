"""Tests for question CRUD, validation, and filter endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from fastapi.testclient import TestClient


def question_payload() -> dict:
    return {
        "question_text": "Which framework is used to build this quiz API?",
        "category": "fastapi",
        "difficulty": "beginner",
        "explanation": "The backend is implemented using FastAPI.",
        "choices": [
          {"choice_text": "Django", "is_correct": False},
          {"choice_text": "FastAPI", "is_correct": True},
          {"choice_text": "Laravel", "is_correct": False},
        ],
    }


def test_create_and_get_question(client: TestClient) -> None:
    create_response = client.post("/questions", json=question_payload())
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] == 1
    assert len(created["choices"]) == 3

    get_response = client.get("/questions/1")
    assert get_response.status_code == 200
    assert get_response.json()["question_text"] == question_payload()["question_text"]


def test_nested_question_requires_one_correct_choice(client: TestClient) -> None:
    payload = question_payload()
    payload["choices"][1]["is_correct"] = False
    response = client.post("/questions", json=payload)
    assert response.status_code == 422
    assert "exactly one correct choice" in response.text


def test_nested_question_requires_multiple_choices(client: TestClient) -> None:
    payload = question_payload()
    payload["choices"] = [{"choice_text": "Only One Choice", "is_correct": True}]
    response = client.post("/questions", json=payload)
    assert response.status_code == 422
    assert "at least two choices" in response.text


def test_nested_question_rejects_duplicate_choices(client: TestClient) -> None:
    payload = question_payload()
    payload["choices"][0]["choice_text"] = "FastAPI"  # Matches choice[1]
    response = client.post("/questions", json=payload)
    assert response.status_code == 422
    assert "Choice text must be unique" in response.text


def test_rejects_invalid_category(client: TestClient) -> None:
    payload = question_payload()
    payload["category"] = "invalid_category_name"
    response = client.post("/questions", json=payload)
    assert response.status_code == 422


def test_rejects_invalid_difficulty(client: TestClient) -> None:
    payload = question_payload()
    payload["difficulty"] = "easy"  # 'easy' is no longer valid, must be 'beginner'
    response = client.post("/questions", json=payload)
    assert response.status_code == 422


def test_prevent_duplicate_questions(client: TestClient) -> None:
    # First post is OK
    res1 = client.post("/questions", json=question_payload())
    assert res1.status_code == 201

    # Second post with identical text raises 409
    res2 = client.post("/questions", json=question_payload())
    assert res2.status_code == 409
    assert res2.json()["detail"] == "A question with the same text already exists."


def test_update_and_delete_question(client: TestClient) -> None:
    client.post("/questions", json=question_payload())
    update_response = client.put(
        "/questions/1", json={"difficulty": "advanced", "category": "python"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["difficulty"] == "advanced"
    assert update_response.json()["category"] == "python"

    delete_response = client.delete("/questions/1")
    assert delete_response.status_code == 200
    assert client.get("/questions/1").status_code == 404
    assert client.get("/choices").json() == []


def test_category_and_difficulty_filters(client: TestClient) -> None:
    # Add Python beginner question
    client.post("/questions", json={
        "question_text": "What is Python?",
        "category": "python",
        "difficulty": "beginner",
        "choices": [
            {"choice_text": "A programming language", "is_correct": True},
            {"choice_text": "A snake", "is_correct": False}
        ]
    })
    # Add Machine Learning intermediate question
    client.post("/questions", json={
        "question_text": "What is Supervised Learning?",
        "category": "machine_learning",
        "difficulty": "intermediate",
        "choices": [
            {"choice_text": "Learning with labeled data", "is_correct": True},
            {"choice_text": "Learning without labeled data", "is_correct": False}
        ]
    })

    # Filter by category
    py_res = client.get("/questions?category=python")
    assert len(py_res.json()) == 1
    assert py_res.json()[0]["question_text"] == "What is Python?"

    # Filter by difficulty
    diff_res = client.get("/questions?difficulty=intermediate")
    assert len(diff_res.json()) == 1
    assert diff_res.json()[0]["question_text"] == "What is Supervised Learning?"


def test_dataset_json_file_is_valid() -> None:
    json_path = Path(__file__).resolve().parent.parent / "data" / "quiz_questions.json"
    assert json_path.exists(), "Dataset file does not exist."
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 30, "Should have 30+ questions in dataset."

"""Tests for choice CRUD and validation endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def create_empty_question(client: TestClient) -> int:
    response = client.post(
        "/questions",
        json={
            "question_text": "What does API stand for in software development?",
            "category": "fastapi",
            "difficulty": "beginner",
            "choices": [],
        },
    )
    return response.json()["id"]


def test_create_update_and_delete_choice(client: TestClient) -> None:
    question_id = create_empty_question(client)
    response = client.post(
        "/choices",
        json={
            "question_id": question_id,
            "choice_text": "Application Programming Interface",
            "is_correct": True,
        },
    )
    assert response.status_code == 201
    choice_id = response.json()["id"]

    update_response = client.put(
        f"/choices/{choice_id}",
        json={"choice_text": "Application Programming Interface (API)"},
    )
    assert update_response.status_code == 200

    delete_response = client.delete(f"/choices/{choice_id}")
    assert delete_response.status_code == 200
    assert client.get(f"/choices/{choice_id}").status_code == 404


def test_prevent_multiple_correct_choices(client: TestClient) -> None:
    question_id = create_empty_question(client)
    first = client.post(
        "/choices",
        json={"question_id": question_id, "choice_text": "Answer A", "is_correct": True},
    )
    assert first.status_code == 201

    second = client.post(
        "/choices",
        json={"question_id": question_id, "choice_text": "Answer B", "is_correct": True},
    )
    assert second.status_code == 400
    assert second.json()["detail"] == "This question already has a correct choice."


def test_cascade_deletion(client: TestClient) -> None:
    # 1. Create a question with choices
    create_response = client.post(
        "/questions",
        json={
            "question_text": "Which cloud service provides virtual machines?",
            "category": "cloud",
            "difficulty": "beginner",
            "choices": [
                {"choice_text": "EC2", "is_correct": True},
                {"choice_text": "S3", "is_correct": False}
            ]
        }
    )
    assert create_response.status_code == 201
    question_id = create_response.json()["id"]
    choices = create_response.json()["choices"]
    assert len(choices) == 2
    choice_ids = [c["id"] for c in choices]

    # 2. Verify choices exist in DB
    for cid in choice_ids:
        assert client.get(f"/choices/{cid}").status_code == 200

    # 3. Delete the question
    del_res = client.delete(f"/questions/{question_id}")
    assert del_res.status_code == 200

    # 4. Verify choices are deleted (cascade)
    for cid in choice_ids:
        assert client.get(f"/choices/{cid}").status_code == 404

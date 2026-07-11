"""Enums for quiz difficulty and category validation."""

from __future__ import annotations

from enum import Enum


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class QuizCategory(str, Enum):
    PYTHON = "python"
    SQL = "sql"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    DEEP_LEARNING = "deep_learning"
    FASTAPI = "fastapi"
    CLOUD = "cloud"
    GENERATIVE_AI = "generative_ai"
    AGENTIC_AI = "agentic_ai"
    DSA = "dsa"

"""Pydantic request and response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.enums import Difficulty, QuizCategory


class ChoiceBase(BaseModel):
    choice_text: str = Field(min_length=1, max_length=300)
    is_correct: bool = False


class ChoiceCreate(ChoiceBase):
    question_id: int = Field(gt=0)


class ChoiceNestedCreate(ChoiceBase):
    pass


class ChoiceUpdate(BaseModel):
    choice_text: str | None = Field(default=None, min_length=1, max_length=300)
    is_correct: bool | None = None


class ChoiceRead(ChoiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int


class QuestionBase(BaseModel):
    question_text: str = Field(min_length=5, max_length=500)
    category: QuizCategory = Field(default=QuizCategory.PYTHON)
    difficulty: Difficulty = Difficulty.INTERMEDIATE
    explanation: str | None = Field(default=None, max_length=2000)


class QuestionCreate(QuestionBase):
    choices: list[ChoiceNestedCreate] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def validate_nested_choices(self) -> "QuestionCreate":
        if self.choices:
            if len(self.choices) < 2:
                raise ValueError("A question must contain at least two choices.")
            correct_count = sum(choice.is_correct for choice in self.choices)
            if correct_count != 1:
                raise ValueError("A question must contain exactly one correct choice.")
            normalized = [choice.choice_text.strip().casefold() for choice in self.choices]
            if len(normalized) != len(set(normalized)):
                raise ValueError("Choice text must be unique within a question.")
        return self


class QuestionUpdate(BaseModel):
    question_text: str | None = Field(default=None, min_length=5, max_length=500)
    category: QuizCategory | None = Field(default=None)
    difficulty: Difficulty | None = None
    explanation: str | None = Field(default=None, max_length=2000)


class QuestionRead(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    choices: list[ChoiceRead] = Field(default_factory=list)


class MessageResponse(BaseModel):
    message: str


class PublicChoice(BaseModel):
    id: int
    choice_text: str


class QuizQuestion(BaseModel):
    id: int
    question_text: str
    category: QuizCategory
    difficulty: Difficulty
    choices: list[PublicChoice]


class QuizAnswer(BaseModel):
    question_id: int = Field(gt=0)
    choice_id: int = Field(gt=0)


class QuizSubmission(BaseModel):
    answers: list[QuizAnswer] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def ensure_unique_questions(self) -> "QuizSubmission":
        question_ids = [answer.question_id for answer in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Only one answer is allowed for each question.")
        return self


class AnswerResult(BaseModel):
    question_id: int
    selected_choice_id: int
    correct_choice_id: int
    is_correct: bool
    explanation: str | None = None


class QuizResult(BaseModel):
    total_questions: int
    correct_answers: int
    wrong_answers: int
    percentage: float
    results: list[AnswerResult]

# Celebal Quiz Backend Management API

A complete RESTful backend project built with **FastAPI, SQLAlchemy, Pydantic, and SQLite** for a Celebal internship. It supports question/choice CRUD operations, validation rules, category and difficulty filters, random quiz generation, quiz scoring, database seeding, automated tests, Swagger documentation, and Docker deployment.

---

## 1. Project Structure

```text
celebal_quiz_backend/
├── app/
│   ├── routers/
│   │   ├── choices.py
│   │   ├── questions.py
│   │   └── quiz.py
│   ├── crud.py
│   ├── database.py
│   ├── enums.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── data/
│   └── quiz_questions.json
├── scripts/
│   └── seed_database.py
├── tests/
│   ├── conftest.py
│   ├── test_choices.py
│   ├── test_questions.py
│   └── test_quiz.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.bat
└── run.sh
```

---

## 2. Setup and Execution

### Windows Setup

```powershell
pip install -r requirements.txt
python scripts/seed_database.py
uvicorn app.main:app --reload
```

### Linux/macOS Setup

```bash
pip install -r requirements.txt
python scripts/seed_database.py
uvicorn app.main:app --reload
```

---

## 3. Dataset Configuration

### File Location
The database dataset file is stored as a JSON array under:
`data/quiz_questions.json`

### Dataset Structure
Each question record in the dataset is defined using the following JSON fields:
```json
{
  "text": "Which Python function converts a string to all lowercase characters?",
  "category": "python",
  "difficulty": "beginner",
  "explanation": "The lower() method returns a copy of the string with all case-based characters lowercased.",
  "choices": [
    {"text": "casefold()", "is_correct": false},
    {"text": "lower()", "is_correct": true},
    {"text": "strip()", "is_correct": false},
    {"text": "upper()", "is_correct": false}
  ]
}
```

### Supported Categories (Enums)
All category fields must reside within the defined `QuizCategory` enum (`app/enums.py`):
- `python`
- `sql`
- `data_science`
- `machine_learning`
- `deep_learning`
- `fastapi`
- `cloud`
- `generative_ai`
- `agentic_ai`

### Supported Difficulty Levels
All difficulty fields must match the `Difficulty` enum:
- `beginner`
- `intermediate`
- `advanced`

---

## 4. Validation Rules

Every quiz question undergoes strict Pydantic validation:
1. **Question text**: Must be clear, meaningful, and between 5 and 500 characters.
2. **Category**: Must match a lowercase `QuizCategory` value.
3. **Difficulty**: Must match a lowercase `Difficulty` value.
4. **Choices count**: Each question must contain between 2 and 6 choices.
5. **Exactly one correct answer**: Each question must have exactly one choice with `"is_correct": true`.
6. **No duplicate choices**: Choice texts must be unique within a single question.
7. **No empty values**: Null or empty strings in critical fields are rejected.

---

## 5. Adding Questions & Categories

### To Add a Question:
Open `data/quiz_questions.json` and append a new JSON object adhering to the structure defined in Section 3, then run the database seed command.

### To Add a Category:
1. Open [enums.py](file:///c:/Users/tanis/OneDrive/Desktop/Celebal_Quiz_Backend_FastAPI_Complete/celebal_quiz_backend/app/enums.py).
2. Append the new category string to the `QuizCategory` enum.
3. Append the category to any matching questions in `data/quiz_questions.json`.
4. Re-run `python scripts/seed_database.py` to seed.

---

## 6. Seeding the Database

To seed the SQLite database:
```bash
python scripts/seed_database.py
```

### Seeding Execution Behavior
1. Parses `data/quiz_questions.json`.
2. Validates records with `schemas.QuestionCreate`.
3. Skips exact and duplicate questions based on `question_text` uniqueness.
4. Reports the statistics upon completion.

**Example Output:**
```text
Dataset validation completed.
Questions inserted: 40
Questions skipped: 0
Invalid questions: 1
```

---

## 7. Quiz Privacy and Scoring Logic

### Privacy (Excluding `is_correct`)
When requesting a quiz via `/quiz/start`, the correct-answer flag `is_correct` is omitted. The API returns `QuizQuestion` schemas which only expose options as:
```json
{
  "id": 1,
  "question_text": "Which Python function converts a string to all lowercase characters?",
  "category": "python",
  "difficulty": "beginner",
  "choices": [
    {"id": 1, "choice_text": "casefold()"},
    {"id": 2, "choice_text": "lower()"}
  ]
}
```

### Scoring Logic
On submission via `/quiz/submit`, the backend retrieves the original questions from the database, confirms that the submitted choice exists and belongs to the question, tracks correct/incorrect/skipped questions, and returns a detailed `QuizResult` containing the score percentage, correct answers count, and detailed feedback (including explanations).

---

## 8. Run Tests

To run the automated tests verifying all requirements (such as dataset loading, privacy checks, invalid inputs, and duplicate question logic):

```bash
pytest -v
```

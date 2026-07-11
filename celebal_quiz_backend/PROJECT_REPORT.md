# Project Completion Report

## Project Title
Celebal Quiz Backend Management API using FastAPI

## Objective
Develop a scalable REST API that manages quiz questions and answer choices through CRUD operations while validating data and maintaining relational database integrity.

## Implemented Modules

1. **Question Management**
   - Create questions with or without nested choices
   - List, search, filter, update, and delete questions
   - Cascade-delete associated answer choices

2. **Choice Management**
   - Add choices to existing questions
   - List choices globally or by question
   - Update and delete choices
   - Prevent more than one correct answer per question

3. **Quiz Flow**
   - Generate a random quiz by category and difficulty
   - Hide correct-answer flags from quiz takers
   - Validate submitted answers
   - Calculate correct answers, wrong answers, and percentage

4. **Data Layer**
   - SQLAlchemy ORM models
   - SQLite default database
   - One-to-many Question/Choice relationship
   - Foreign-key and uniqueness constraints

5. **Validation and Error Handling**
   - Pydantic request and response models
   - Minimum/maximum text lengths
   - Exactly one correct choice for nested question creation
   - Meaningful 400, 404, 409, and 422 errors

6. **Quality and Deployment**
   - Swagger and ReDoc documentation
   - Automated Pytest tests
   - Seed dataset with 20 technical questions
   - Dockerfile and Docker Compose configuration

## Learning Outcomes Demonstrated

- RESTful API design
- FastAPI routing and dependency injection
- SQLAlchemy 2.x ORM usage
- Pydantic validation
- Relational data modeling
- API testing
- Containerized deployment

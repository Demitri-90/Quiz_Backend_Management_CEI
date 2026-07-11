# Quiz Backend Management API

A RESTful backend application built with **FastAPI** for managing quiz questions and answer choices. The API supports CRUD operations and stores quiz data using a relational database.

## Features

* Create, read, update, and delete quiz questions
* Create, read, update, and delete answer choices
* One-to-many relationship between questions and choices
* Request validation using Pydantic
* Interactive API documentation with Swagger UI

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* Uvicorn

## Getting Started

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
uvicorn main:app --reload
```

## API Documentation

After starting the server, open:

* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

## Project Purpose

This project was developed to demonstrate backend API development using FastAPI, including database integration, CRUD operations, and relational data management for quiz applications.

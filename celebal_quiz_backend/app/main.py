"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 - ensures models are registered
from app.database import Base, engine
from app.routers import choices, questions, quiz


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Celebal Quiz Backend Management API",
    version="1.0.0",
    description=(
        "A RESTful FastAPI backend for managing quiz questions and choices, "
        "starting quizzes, and calculating scores."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(choices.router)
app.include_router(quiz.router)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "message": "Celebal Quiz Backend API is running.",
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}

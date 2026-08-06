"""
Entry point for the backend API.

Run it with:  uvicorn app.main:app --reload --port 8000
(from inside the backend/ folder, with your virtual environment active)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import saved_connections

from app.core.config import settings
from app.api import connections

app = FastAPI(
    title=settings.APP_NAME,
    description="Read-only AI database analysis and report generation API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connections.router)
app.include_router(saved_connections.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
def root():
    return {"message": "DBReport AI backend is running. See /docs for the API explorer."}

"""
Entry point for the backend API.

Run it with:  uvicorn app.main:app --reload --port 8000
(from inside the backend/ folder, with your virtual environment active)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Read-only AI database analysis and report generation API",
    version="0.1.0",
)

# Without this, the Next.js frontend (running on a different port/origin)
# would be blocked by the browser from calling this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """
    Simple endpoint the frontend calls on load to confirm the backend
    is reachable — the 'hello world' proof that frontend and backend
    are wired together before any real features exist.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
def root():
    return {"message": "DBReport AI backend is running. See /docs for the API explorer."}
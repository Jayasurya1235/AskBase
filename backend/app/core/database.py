"""
Sets up OUR app's own database — a small SQLite file (locally) or
Postgres database (in production) that stores things like saved
connections, saved reports, and (later) user accounts.

This is completely separate from the databases users connect to for
analysis (chinook, their MySQL/Postgres, etc). Think of it as
"AskBase's own filing cabinet" vs. "the customer's database we're
allowed to read from."
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Locally, falls back to a SQLite file, askbase.db, in the backend/ folder.
# In production, DATABASE_URL is set to a real Postgres connection string.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./askbase.db")

# Some hosts (Render, Heroku-style) hand out "postgres://" URLs, but
# SQLAlchemy 2.0 requires "postgresql://". Fix it up if needed.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs this extra arg for FastAPI's threaded requests; Postgres
# doesn't accept it at all, so only pass it when we're actually on SQLite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every model (like SavedConnection) inherits from this Base, which is
# how SQLAlchemy knows what tables to create.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency: provides a database session for a single request,
    and guarantees it's closed afterward — even if the request errors out.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
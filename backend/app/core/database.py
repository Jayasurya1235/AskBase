"""
Sets up OUR app's own database — a small SQLite file that stores things
like saved connections, saved reports, and (later) user accounts.

This is completely separate from the databases users connect to for
analysis (chinook, their MySQL/Postgres, etc). Think of it as
"AskBase's own filing cabinet" vs. "the customer's database we're
allowed to read from."
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# A single file, askbase.db, created in the backend/ folder the first
# time the app runs. No separate database server needed for this.
DATABASE_URL = "sqlite:///./askbase.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
)

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
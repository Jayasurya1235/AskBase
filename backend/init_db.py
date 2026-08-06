"""
One-time script to create the database file and all its tables.

Run it with:  python init_db.py
(from inside backend/, with venv active)

You only need to run this once (or again later if you add a brand new
model — for changing existing tables, we'd use Alembic migrations, but
that's a later concern).
"""

from app.core.database import Base, engine
from app.models.saved_connection import SavedConnection  # noqa: F401 (import registers the table)

Base.metadata.create_all(bind=engine)

print("Database initialized: askbase.db created with saved_connections table.")
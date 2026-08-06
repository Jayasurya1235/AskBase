"""
SQLAlchemy model for a saved database connection.

This is OUR app's own storage table — completely separate from the
user's actual databases (chinook, etc). It only stores metadata about
how to reconnect: host, port, username, and an ENCRYPTED password.
The raw password is never written to disk in plain text.
"""

from sqlalchemy import Column, Integer, String
from app.core.database import Base


class SavedConnection(Base):
    __tablename__ = "saved_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)          # e.g. "My Shop DB"
    db_type = Column(String, nullable=False)        # "mysql" or "postgresql"
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)  # never plain text
    database = Column(String, nullable=False)
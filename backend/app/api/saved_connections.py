"""
Routes for saving and retrieving database connections.

Passwords are encrypted before being written to our own askbase.db —
never stored in plain text.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import encrypt_text
from app.models.saved_connection import SavedConnection
from app.models.connection import DatabaseConnectionRequest

router = APIRouter(prefix="/saved-connections", tags=["saved-connections"])


@router.post("/")
def save_connection(
    name: str,
    request: DatabaseConnectionRequest,
    db: Session = Depends(get_db),
):
    """
    Saves a database connection for later reuse. The password is
    encrypted before it's written to disk.
    """
    new_connection = SavedConnection(
        name=name,
        db_type=request.db_type,
        host=request.host,
        port=request.port,
        username=request.username,
        encrypted_password=encrypt_text(request.password),
        database=request.database,
    )

    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)

    return {
        "id": new_connection.id,
        "name": new_connection.name,
        "message": "Connection saved successfully.",
    }


@router.get("/")
def list_connections(db: Session = Depends(get_db)):
    """
    Returns all saved connections — WITHOUT decrypting passwords.
    The frontend only needs to show a list to pick from; the actual
    password is decrypted server-side only when reconnecting.
    """
    connections = db.query(SavedConnection).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "db_type": c.db_type,
            "host": c.host,
            "database": c.database,
        }
        for c in connections
    ]
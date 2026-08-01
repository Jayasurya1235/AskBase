"""
Routes for database connection testing.

Keeps this file thin on purpose — it just receives the request,
hands it to the service layer (database_connector.py) to do the
actual work, and returns the result. All real logic lives in services/.
"""

from fastapi import APIRouter

from app.models.connection import DatabaseConnectionRequest, DatabaseConnectionResponse
from app.services.database_connector import test_connection

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("/test", response_model=DatabaseConnectionResponse)
def test_database_connection(request: DatabaseConnectionRequest):
    """
    Accepts database credentials submitted by the user (not from .env)
    and attempts a real, read-only connection to confirm they work.
    """
    return test_connection(request)

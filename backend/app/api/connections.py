"""
Routes for database connection testing and schema introspection.

Keeps this file thin on purpose — it just receives the request,
hands it to the service layer to do the actual work, and returns the
result. All real logic lives in services/.
"""

from fastapi import APIRouter

from app.models.connection import DatabaseConnectionRequest, DatabaseConnectionResponse
from app.models.schema import SchemaResponse
from app.services.database_connector import test_connection
from app.services.schema_inspector import inspect_schema

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("/test", response_model=DatabaseConnectionResponse)
def test_database_connection(request: DatabaseConnectionRequest):
    """
    Accepts database credentials submitted by the user (not from .env)
    and attempts a real, read-only connection to confirm they work.
    """
    return test_connection(request)


@router.post("/schema", response_model=SchemaResponse)
def get_database_schema(request: DatabaseConnectionRequest):
    """
    Connects to the given database and returns its full schema:
    tables, columns, and foreign key relationships. This is what
    the AI (Phase 4) will use to understand what it's querying.
    """
    return inspect_schema(request)
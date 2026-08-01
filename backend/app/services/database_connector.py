"""
Handles testing a database connection dynamically, using credentials
that arrive fresh in each request (never from .env, never hardcoded).

This is what makes the app multi-database: every call to
test_connection() can point at a completely different database, because
everything it needs is passed in as arguments.
"""

from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.models.connection import DatabaseConnectionRequest, DatabaseConnectionResponse


def build_connection_url(request: DatabaseConnectionRequest) -> str:
    safe_username = quote_plus(request.username)
    safe_password = quote_plus(request.password)

    if request.db_type == "mysql":
        return (
            f"mysql+pymysql://{safe_username}:{safe_password}"
            f"@{request.host}:{request.port}/{request.database}"
        )
    elif request.db_type == "postgresql":
        return (
            f"postgresql+psycopg2://{safe_username}:{safe_password}"
            f"@{request.host}:{request.port}/{request.database}"
        )
    else:
        raise ValueError(f"Unsupported database type: {request.db_type}")


def test_connection(request: DatabaseConnectionRequest) -> DatabaseConnectionResponse:
    try:
        connection_url = build_connection_url(request)
        engine = create_engine(connection_url, connect_args={"connect_timeout": 5})

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return DatabaseConnectionResponse(
            success=True,
            message=f"Successfully connected to {request.database} ({request.db_type})",
        )

    except SQLAlchemyError as e:
        return DatabaseConnectionResponse(
            success=False,
            message=f"Connection failed: {str(e.__cause__ or e)}",
        )

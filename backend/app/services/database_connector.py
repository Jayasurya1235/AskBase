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
    if request.db_type == "sqlite":
        # SQLite has no host/user/password — database is a file path.
        return f"sqlite:///{request.database}"

    # URL-encode username and password so special characters like @, #, :
    # don't get misread as part of the URL's structure.
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

        if request.db_type == "sqlite":
            connect_args = {}
        elif request.db_type == "postgresql":
            # Cloud Postgres providers (Supabase, RDS, Neon, etc.) typically
            # require an encrypted connection.
            connect_args = {"connect_timeout": 10, "sslmode": "require"}
        else:
            connect_args = {"connect_timeout": 10}

        engine = create_engine(connection_url, connect_args=connect_args)

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

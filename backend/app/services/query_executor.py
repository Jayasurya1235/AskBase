"""
Executes validated, read-only SQL against the user's database and
returns the results as plain Python data (columns + rows).

This only ever runs SQL that has already passed through
sql_validator.py — this file assumes the SQL is safe and focuses
purely on execution and row-limiting.
"""

from sqlalchemy import create_engine, text

from app.models.connection import DatabaseConnectionRequest
from app.services.database_connector import build_connection_url

# Hard safety cap: never return more rows than this to the frontend,
# regardless of what the query itself requests. Protects against
# accidentally (or maliciously) huge result sets.
MAX_ROWS = 500


def execute_query(sql: str, connection: DatabaseConnectionRequest):
    """
    Runs the given SQL against the connected database and returns
    (columns, rows, row_count).
    """
    connection_url = build_connection_url(connection)
    engine = create_engine(connection_url, connect_args={"connect_timeout": 5})

    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())

        rows = []
        for i, row in enumerate(result):
            if i >= MAX_ROWS:
                break
            rows.append(dict(zip(columns, row)))

        return columns, rows, len(rows)
    
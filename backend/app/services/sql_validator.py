"""
Validates that a piece of SQL is safe to execute: exactly one
statement, and that statement is a SELECT — nothing else.

This is the real enforcement of the app's "read-only" guarantee.
We never trust AI-generated SQL just because we asked nicely in the
prompt — this is the actual gate before anything touches a database.
"""

import sqlglot
from sqlglot import exp


class UnsafeSQLError(Exception):
    """Raised when generated SQL fails the safety check."""
    pass


_DIALECT_MAP = {
    "postgresql": "postgres",
    "mysql": "mysql",
    "sqlite": "sqlite",
}


def validate_sql(sql: str, dialect: str = "mysql") -> str:
    """
    Parses the SQL and raises UnsafeSQLError if it's anything other
    than a single SELECT statement. Returns the cleaned SQL if valid.
    """
    sqlglot_dialect = _DIALECT_MAP.get(dialect, dialect)

    try:
        parsed_statements = sqlglot.parse(sql, read=sqlglot_dialect)
    except Exception as e:
        raise UnsafeSQLError(f"Could not parse SQL: {e}")

    # Reject empty or multi-statement input (e.g. "SELECT 1; DROP TABLE x;")
    statements = [s for s in parsed_statements if s is not None]

    if len(statements) == 0:
        raise UnsafeSQLError("No valid SQL statement found.")

    if len(statements) > 1:
        raise UnsafeSQLError("Multiple SQL statements are not allowed.")

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise UnsafeSQLError(
            f"Only SELECT statements are allowed. Got: {type(statement).__name__}"
        )
    

    # Defense in depth: even within a SELECT, reject any subquery or
    # clause that references data-modifying constructs.
    forbidden_types = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter, exp.Create)
    for node in statement.walk():
        if isinstance(node[0], forbidden_types):
            raise UnsafeSQLError("Query contains a disallowed operation.")

    return statement.sql(dialect=sqlglot_dialect)
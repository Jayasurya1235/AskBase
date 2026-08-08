"""
Routes for asking natural-language questions, generating and
validating SQL, executing it, and returning real results.
"""

from fastapi import APIRouter, HTTPException

from app.models.query import AskQuestionRequest, AskQuestionResponse
from app.services.schema_inspector import inspect_schema
from app.services.text_to_sql import generate_sql
from app.services.sql_validator import validate_sql, UnsafeSQLError
from app.services.query_executor import execute_query

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/ask", response_model=AskQuestionResponse)
def ask_question(request: AskQuestionRequest):
    """
    Full pipeline: question -> schema -> generated SQL -> validated
    SQL -> executed against the database -> real results returned.
    """
    schema = inspect_schema(request.connection)
    raw_sql = generate_sql(request.question, schema)

    try:
        safe_sql = validate_sql(raw_sql, dialect=request.connection.db_type)
    except UnsafeSQLError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Generated SQL failed safety validation: {e}",
        )

    try:
        columns, rows, row_count = execute_query(safe_sql, request.connection)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {e}",
        )

    return AskQuestionResponse(
        question=request.question,
        generated_sql=safe_sql,
        columns=columns,
        rows=rows,
        row_count=row_count,
    )
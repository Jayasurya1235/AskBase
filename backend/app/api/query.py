"""
Routes for asking natural-language questions and getting back
validated SQL. Execution of that SQL comes in Phase 5.
"""

from fastapi import APIRouter, HTTPException

from app.models.query import AskQuestionRequest, AskQuestionResponse
from app.services.schema_inspector import inspect_schema
from app.services.text_to_sql import generate_sql
from app.services.sql_validator import validate_sql, UnsafeSQLError

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/ask", response_model=AskQuestionResponse)
def ask_question(request: AskQuestionRequest):
    """
    Takes a plain-English question and connection details, reads the
    database's schema, generates SQL, and validates it before
    returning — guaranteeing only safe SELECT statements ever leave
    this endpoint.
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

    return AskQuestionResponse(question=request.question, generated_sql=safe_sql)
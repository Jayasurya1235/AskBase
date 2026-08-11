"""
Routes for asking questions — either meta questions about the
database's structure/capabilities (answered directly) or data
questions (SQL generated, validated, executed, and summarized in
plain English).
"""

from fastapi import APIRouter, HTTPException

from app.models.query import AskQuestionRequest, AskQuestionResponse
from app.services.schema_inspector import inspect_schema
from app.services.text_to_sql import generate_sql
from app.services.sql_validator import validate_sql, UnsafeSQLError
from app.services.query_executor import execute_query
from app.services.query_router import (
    classify_intent,
    answer_meta_question,
    summarize_data_answer,
)

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/ask", response_model=AskQuestionResponse)
def ask_question(request: AskQuestionRequest):
    schema = inspect_schema(request.connection)
    intent = classify_intent(request.question, schema)

    if intent == "meta":
        answer = answer_meta_question(request.question, schema)
        return AskQuestionResponse(
            question=request.question,
            answer=answer,
            query_type="meta",
        )

    # intent == "data"
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
        raise HTTPException(status_code=500, detail=f"Query execution failed: {e}")

    answer = summarize_data_answer(request.question, columns, rows)

    return AskQuestionResponse(
        question=request.question,
        answer=answer,
        query_type="data",
        generated_sql=safe_sql,
        columns=columns,
        rows=rows,
        row_count=row_count,
    )
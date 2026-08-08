"""
Routes for asking natural-language questions and getting back
generated SQL. Execution of that SQL comes in Phase 5 — this endpoint
only generates and returns the query text.
"""

from fastapi import APIRouter

from app.models.query import AskQuestionRequest, AskQuestionResponse
from app.services.schema_inspector import inspect_schema
from app.services.text_to_sql import generate_sql

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/ask", response_model=AskQuestionResponse)
def ask_question(request: AskQuestionRequest):
    """
    Takes a plain-English question and connection details, reads the
    database's schema, and returns AI-generated SQL that answers it.
    """
    schema = inspect_schema(request.connection)
    sql = generate_sql(request.question, schema)

    return AskQuestionResponse(question=request.question, generated_sql=sql)
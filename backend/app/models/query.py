"""
Defines the shape of a natural-language question request and the
answer generated in response — either a direct answer (for
meta/capability questions) or a data-backed answer with SQL and
results attached (for questions that need real query execution).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.models.connection import DatabaseConnectionRequest


class AskQuestionRequest(BaseModel):
    question: str
    connection: DatabaseConnectionRequest


class AskQuestionResponse(BaseModel):
    question: str
    answer: str
    query_type: str  # "data" or "meta"
    generated_sql: Optional[str] = None
    columns: Optional[List[str]] = None
    rows: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None
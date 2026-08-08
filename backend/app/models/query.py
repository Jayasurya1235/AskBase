"""
Defines the shape of a natural-language question request and the
SQL + results generated in response.
"""

from typing import List, Dict, Any
from pydantic import BaseModel

from app.models.connection import DatabaseConnectionRequest


class AskQuestionRequest(BaseModel):
    question: str
    connection: DatabaseConnectionRequest


class AskQuestionResponse(BaseModel):
    question: str
    generated_sql: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
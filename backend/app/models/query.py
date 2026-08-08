"""
Defines the shape of a natural-language question request and the
SQL generated in response.
"""

from pydantic import BaseModel

from app.models.connection import DatabaseConnectionRequest


class AskQuestionRequest(BaseModel):
    question: str
    connection: DatabaseConnectionRequest


class AskQuestionResponse(BaseModel):
    question: str
    generated_sql: str
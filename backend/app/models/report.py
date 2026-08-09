"""
Defines the shape of a report generation request and its response —
a multi-dimensional data breakdown plus an AI-written narrative
analysis, meant to be displayed as charts + readable text.
"""

from typing import List, Dict, Any
from pydantic import BaseModel

from app.models.connection import DatabaseConnectionRequest


class ReportRequest(BaseModel):
    topic: str  # e.g. "sales by product and area"
    connection: DatabaseConnectionRequest


class ReportResponse(BaseModel):
    topic: str
    generated_sql: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    narrative: str
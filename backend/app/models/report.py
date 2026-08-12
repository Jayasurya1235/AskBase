"""
Defines the shape of a report generation request and its response —
a multi-dimensional data breakdown, per-group best/worst analysis,
and an AI-written narrative, meant to be displayed as charts + text.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.models.connection import DatabaseConnectionRequest


class ReportRequest(BaseModel):
    topic: str
    connection: DatabaseConnectionRequest


class ReportResponse(BaseModel):
    topic: str
    generated_sql: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    narrative: str
    kpis: Optional[Dict[str, Any]] = None
    top_per_group: Optional[List[Dict[str, Any]]] = None
    bottom_per_group: Optional[List[Dict[str, Any]]] = None
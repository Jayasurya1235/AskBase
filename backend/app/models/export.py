"""
Defines the shape of an export request — takes results the frontend
already has (from a completed /query/ask call) and turns them into
a downloadable file. No re-querying the database needed.
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class ExportRequest(BaseModel):
    question: str
    columns: List[str]
    rows: List[Dict[str, Any]]
"""
Defines the shape of an export request — takes results the frontend
already has and turns them into a downloadable file.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ExportRequest(BaseModel):
    question: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    narrative: Optional[str] = None
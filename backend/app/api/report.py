"""
Routes for generating full analytical reports: multi-dimensional
data + AI-written narrative analysis.
"""

from fastapi import APIRouter, HTTPException

from app.models.report import ReportRequest, ReportResponse
from app.services.report_generator import generate_report
from app.services.sql_validator import UnsafeSQLError

router = APIRouter(prefix="/report", tags=["report"])


@router.post("/generate", response_model=ReportResponse)
def generate_report_endpoint(request: ReportRequest):
    """
    Takes a report topic and connection details, generates a
    two-dimensional breakdown query, validates and executes it, and
    returns the data alongside an AI-written narrative analysis.
    """
    try:
        sql, columns, rows, row_count, narrative = generate_report(
            request.topic, request.connection
        )
    except UnsafeSQLError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Generated SQL failed safety validation: {e}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

    return ReportResponse(
        topic=request.topic,
        generated_sql=sql,
        columns=columns,
        rows=rows,
        row_count=row_count,
        narrative=narrative,
    )
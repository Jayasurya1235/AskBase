"""
Routes for exporting query results as downloadable Excel or PDF files.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.export import ExportRequest
from app.services.export_service import generate_excel, generate_pdf

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/excel")
def export_excel(request: ExportRequest):
    buffer = generate_excel(request)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=askbase_export.xlsx"},
    )


@router.post("/pdf")
def export_pdf(request: ExportRequest):
    buffer = generate_pdf(request)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=askbase_export.pdf"},
    )
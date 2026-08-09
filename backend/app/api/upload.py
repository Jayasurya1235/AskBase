"""
Route for uploading a CSV/Excel file and converting it into a
queryable SQLite-backed connection.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.file_upload import convert_file_to_sqlite

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts a CSV or Excel file, converts it to a SQLite database,
    and returns a connection object the frontend can use exactly like
    any other database connection (db_type="sqlite").
    """
    try:
        contents = await file.read()
        db_path = convert_file_to_sqlite(file.filename, contents)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

    return {
        "db_type": "sqlite",
        "host": "",
        "port": 0,
        "username": "",
        "password": "",
        "database": db_path,
        "message": f"Successfully imported {file.filename}",
    }
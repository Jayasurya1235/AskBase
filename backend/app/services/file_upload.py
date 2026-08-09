"""
Converts an uploaded CSV or Excel file into a SQLite database file,
so the rest of the app (schema inspection, chat, reports) can treat
it exactly like any other connected database — no separate code path
needed for "files" vs "real databases."
"""

import os
import uuid

import pandas as pd
from sqlalchemy import create_engine

# Uploaded files become SQLite databases stored here. In a real
# production app this would be per-user and cleaned up periodically —
# for this project, a local folder is a reasonable, simple choice.
UPLOAD_DIR = "uploaded_dbs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def convert_file_to_sqlite(filename: str, file_bytes: bytes) -> str:
    """
    Reads a CSV or Excel file's contents, writes it into a new SQLite
    database as a single table, and returns the path to that database
    file — this path becomes the `database` field in a connection
    request with db_type="sqlite".
    """
    extension = filename.rsplit(".", 1)[-1].lower()

    import io
    buffer = io.BytesIO(file_bytes)

    if extension == "csv":
        df = pd.read_csv(buffer)
    elif extension in ("xlsx", "xls"):
        df = pd.read_excel(buffer)
    else:
        raise ValueError(f"Unsupported file type: .{extension}")

    # Clean column names: SQL doesn't like spaces or special characters
    # in identifiers, so replace them with underscores.
    df.columns = [
        str(col).strip().replace(" ", "_").replace("-", "_") for col in df.columns
    ]

    db_filename = f"{UPLOAD_DIR}/{uuid.uuid4().hex}.db"
    engine = create_engine(f"sqlite:///{db_filename}")

    # The table is always named "data" — simple and predictable, since
    # a single-file upload only ever produces one table.
    df.to_sql("data", engine, if_exists="replace", index=False)

    return db_filename
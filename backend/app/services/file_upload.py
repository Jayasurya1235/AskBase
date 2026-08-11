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

    import re

    # Clean column names aggressively: keep only letters, digits, and
    # underscores. Messy source files can contain title rows, em-dashes,
    # or even stray control characters (e.g. from copy-pasted terminal
    # output) — none of that is valid in a SQL identifier.
    def clean_column_name(name: str) -> str:
        name = str(name).strip()
        name = re.sub(r"[^\w]+", "_", name)  # anything not letter/digit/underscore -> _
        name = re.sub(r"_+", "_", name).strip("_")  # collapse repeats, trim edges
        return name or "column"

    df.columns = [clean_column_name(col) for col in df.columns]

    # If the resulting names collide (common with messy "Unnamed" columns),
    # make them unique by appending a number.
    seen = {}
    unique_columns = []
    for col in df.columns:
        if col in seen:
            seen[col] += 1
            unique_columns.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            unique_columns.append(col)
    df.columns = unique_columns

    db_filename = f"{UPLOAD_DIR}/{uuid.uuid4().hex}.db"
    engine = create_engine(f"sqlite:///{db_filename}")

    # The table is always named "data" — simple and predictable, since
    # a single-file upload only ever produces one table.
    df.to_sql("data", engine, if_exists="replace", index=False)

    return db_filename
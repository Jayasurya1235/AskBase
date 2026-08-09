"""
Defines the shape of data going in and out of the connection-testing
endpoint. Pydantic validates this automatically — if the frontend sends
a request missing a field, or with the wrong type (e.g. port as text
instead of a number), FastAPI rejects it before our code even runs.
"""

from pydantic import BaseModel
from typing import Literal


from typing import Optional


class DatabaseConnectionRequest(BaseModel):
    db_type: Literal["mysql", "postgresql", "sqlite"]
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    database: str  # for sqlite, this is the file path instead of a db name


class DatabaseConnectionResponse(BaseModel):
    success: bool
    message: str

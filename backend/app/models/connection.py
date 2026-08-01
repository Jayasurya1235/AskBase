"""
Defines the shape of data going in and out of the connection-testing
endpoint. Pydantic validates this automatically — if the frontend sends
a request missing a field, or with the wrong type (e.g. port as text
instead of a number), FastAPI rejects it before our code even runs.
"""

from pydantic import BaseModel
from typing import Literal


class DatabaseConnectionRequest(BaseModel):
    db_type: Literal["mysql", "postgresql"]
    host: str
    port: int
    username: str
    password: str
    database: str


class DatabaseConnectionResponse(BaseModel):
    success: bool
    message: str

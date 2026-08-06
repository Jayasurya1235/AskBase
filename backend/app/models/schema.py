"""
Defines the shape of schema information returned after inspecting a
connected database — what tables exist, what columns they have, and
how tables relate to each other via foreign keys.
"""

from pydantic import BaseModel
from typing import List


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool


class ForeignKeyInfo(BaseModel):
    column: str
    references_table: str
    references_column: str


class TableInfo(BaseModel):
    name: str
    columns: List[ColumnInfo]
    foreign_keys: List[ForeignKeyInfo]


class SchemaResponse(BaseModel):
    database: str
    tables: List[TableInfo]
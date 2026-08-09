"""
Reads the real structure of a connected database — tables, columns,
and foreign key relationships — using SQLAlchemy's Inspector.

This works generically for any database SQLAlchemy supports; nothing
here is hardcoded to chinook or MySQL specifically.
"""

from sqlalchemy import create_engine, inspect

from app.models.connection import DatabaseConnectionRequest
from app.models.schema import SchemaResponse, TableInfo, ColumnInfo, ForeignKeyInfo
from app.services.database_connector import build_connection_url


def inspect_schema(request: DatabaseConnectionRequest) -> SchemaResponse:
    """
    Connects to the given database and reads its full schema:
    every table, every column (with type/nullable/primary key), and
    every foreign key relationship between tables.
    """
    connection_url = build_connection_url(request)
    connect_args = {} if request.db_type == "sqlite" else {"connect_timeout": 5}
    engine = create_engine(connection_url, connect_args=connect_args)
    inspector = inspect(engine)

    tables = []

    for table_name in inspector.get_table_names():
        # Columns
        columns = []
        pk_columns = set(inspector.get_pk_constraint(table_name)["constrained_columns"])

        for col in inspector.get_columns(table_name):
            columns.append(
                ColumnInfo(
                    name=col["name"],
                    type=str(col["type"]),
                    nullable=col["nullable"],
                    primary_key=col["name"] in pk_columns,
                )
            )

        # Foreign keys
        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            # A foreign key can technically span multiple columns; we
            # handle the common single-column case here.
            if fk["constrained_columns"] and fk["referred_columns"]:
                foreign_keys.append(
                    ForeignKeyInfo(
                        column=fk["constrained_columns"][0],
                        references_table=fk["referred_table"],
                        references_column=fk["referred_columns"][0],
                    )
                )

        tables.append(
            TableInfo(name=table_name, columns=columns, foreign_keys=foreign_keys)
        )

    return SchemaResponse(database=request.database, tables=tables)
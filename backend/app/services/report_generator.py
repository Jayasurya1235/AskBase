"""
Generates a full report: multi-dimensional SQL query + per-group
best/worst breakdown + AI-written narrative analysis of the results.

Reuses the existing text-to-SQL, validation, and execution pipeline —
this file adds the "analyze and explain" layer on top.
"""

import pandas as pd
from groq import Groq

from app.core.config import settings
from app.models.schema import SchemaResponse
from app.models.connection import DatabaseConnectionRequest
from app.services.schema_inspector import inspect_schema
from app.services.sql_validator import validate_sql, UnsafeSQLError
from app.services.query_executor import execute_query
from app.services.text_to_sql import _schema_to_text

client = Groq(api_key=settings.GROQ_API_KEY)


def _generate_report_sql(topic: str, schema: SchemaResponse) -> str:
    schema_text = _schema_to_text(schema)
    table_names = [t.name for t in schema.tables]

    system_prompt = (
        "You are a SQL generator specializing in analytical reports. "
        "Given a database schema and a report topic, write ONE SQL "
        "SELECT query that breaks the data down by TWO dimensions "
        "(e.g. category and location, or product and region) with an "
        "aggregated numeric measure (SUM or COUNT), grouped and ordered "
        "sensibly. Respond with ONLY the raw SQL — no explanation, no "
        "markdown, no code fences. Never generate INSERT, UPDATE, "
        "DELETE, DROP, ALTER, or anything other than SELECT. Only use "
        "tables and columns that exist in the schema."
    )

    user_prompt = (
        f"Available tables (use ONLY these exact names): {table_names}\n\n"
        f"Database name: {schema.database}\n\nSchema:\n{schema_text}\n\n"
        f"Report topic: {topic}\n\nSQL:"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()
    if sql.startswith("```"):
        sql = sql.strip("`")
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()
    return sql


def _compute_group_breakdown(columns: list, rows: list):
    """
    If the result looks like (dimension1, dimension2, measure) — e.g.
    City, Model, Revenue — compute the best and worst performer WITHIN
    each dimension1 group, plus overall KPIs. Returns (kpis, top_per_group,
    bottom_per_group), or (None, None, None) if the shape doesn't fit.
    """
    if len(columns) != 3 or not rows:
        return None, None, None

    df = pd.DataFrame(rows)
    dim1, dim2, measure = columns

    # The measure column must actually be numeric for this to make sense.
    if not pd.api.types.is_numeric_dtype(df[measure]):
        return None, None, None

    kpis = {
        "total": float(df[measure].sum()),
        "row_count": len(df),
        "unique_groups": int(df[dim1].nunique()),
        "top_group": str(df.groupby(dim1)[measure].sum().idxmax()),
        "top_group_value": float(df.groupby(dim1)[measure].sum().max()),
    }

    grouped = df.groupby(dim1)
    top_idx = grouped[measure].idxmax()
    bottom_idx = grouped[measure].idxmin()

    top_per_group = df.loc[top_idx].sort_values(measure, ascending=False).to_dict("records")
    bottom_per_group = df.loc[bottom_idx].sort_values(measure, ascending=True).to_dict("records")

    return kpis, top_per_group, bottom_per_group


def _generate_narrative(topic: str, columns: list, rows: list, kpis, top_per_group, bottom_per_group) -> str:
    sample_rows = rows[:100]

    context_parts = [f"Report topic: {topic}", f"Columns: {columns}", f"Sample data:\n{sample_rows}"]

    if kpis:
        context_parts.append(f"Overall totals: {kpis}")
    if top_per_group:
        context_parts.append(f"Best performer within each group:\n{top_per_group}")
    if bottom_per_group:
        context_parts.append(f"Weakest performer within each group:\n{bottom_per_group}")

    system_prompt = (
        "You are a data analyst writing a report summary. Given tabular "
        "data — and, when available, the best/worst performer within "
        "each group — write a clear, numbered analysis (5-7 points) in "
        "plain English. Call out specific standout figures: highest and "
        "lowest values, notable comparisons BETWEEN groups (e.g. "
        "'City A prefers Model X while City B prefers Model Y'), and any "
        "clear patterns. Always use the real numbers and names given. "
        "Never invent data that isn't present."
    )
    user_prompt = "\n\n".join(context_parts) + "\n\nWrite the analysis:"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def generate_report(topic: str, connection: DatabaseConnectionRequest):
    schema = inspect_schema(connection)
    raw_sql = _generate_report_sql(topic, schema)

    safe_sql = validate_sql(raw_sql, dialect=connection.db_type)

    columns, rows, row_count = execute_query(safe_sql, connection)

    kpis, top_per_group, bottom_per_group = _compute_group_breakdown(columns, rows)

    narrative = _generate_narrative(topic, columns, rows, kpis, top_per_group, bottom_per_group)

    return safe_sql, columns, rows, row_count, narrative, kpis, top_per_group, bottom_per_group
"""
Generates a full report: multi-dimensional SQL query + AI-written
narrative analysis of the results.

Reuses the existing text-to-SQL, validation, and execution pipeline —
this file adds the "analyze and explain" layer on top.
"""

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
    """
    Like generate_sql, but specifically prompted to produce a
    GROUP BY across two dimensions (e.g. product and region) with an
    aggregated measure (e.g. SUM of revenue or quantity) — the shape
    a report needs, rather than a single-answer query.
    """
    schema_text = _schema_to_text(schema)

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


def _generate_narrative(topic: str, columns: list, rows: list) -> str:
    """
    Sends the actual result data back to the AI and asks it to write
    a plain-English analysis — the "article-like" explanation with
    concrete callouts (highest/lowest, comparisons, standout figures).
    """
    # Keep the data payload reasonable in size for the prompt.
    sample_rows = rows[:100]

    system_prompt = (
        "You are a data analyst writing a short report summary. Given "
        "tabular data, write a clear, concise analysis in plain English "
        "using short bullet points. Call out specific standout figures: "
        "highest and lowest values, notable comparisons between "
        "categories, and any clear patterns. Use the actual numbers and "
        "names from the data. Do not invent data that isn't present. "
        "Keep it to 4-6 bullet points."
    )

    user_prompt = (
        f"Report topic: {topic}\n\n"
        f"Columns: {columns}\n\n"
        f"Data:\n{sample_rows}\n\n"
        "Write the analysis:"
    )

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
    """
    Full pipeline: schema -> multi-dimensional SQL -> validate ->
    execute -> AI narrative analysis of the real results.
    """
    schema = inspect_schema(connection)
    raw_sql = _generate_report_sql(topic, schema)

    safe_sql = validate_sql(raw_sql, dialect=connection.db_type)  # raises UnsafeSQLError if unsafe

    columns, rows, row_count = execute_query(safe_sql, connection)

    narrative = _generate_narrative(topic, columns, rows)

    return safe_sql, columns, rows, row_count, narrative
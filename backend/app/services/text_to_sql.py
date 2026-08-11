"""
Converts a plain-English question into a SQL query using Groq's API,
given the target database's schema as context.

Safety note: this only *generates* SQL text. It does not execute
anything. Execution (Phase 5) will run the generated SQL through a
separate validation layer that rejects anything that isn't a single,
safe SELECT statement — we never trust AI output blindly.
"""

from groq import Groq

from app.core.config import settings
from app.models.schema import SchemaResponse

client = Groq(api_key=settings.GROQ_API_KEY)


def _schema_to_text(schema: SchemaResponse) -> str:
    """
    Turns our structured schema object into a compact text description
    the AI can read — table names, columns, and relationships.
    """
    lines = []
    for table in schema.tables:
        columns_desc = ", ".join(f"{c.name} ({c.type})" for c in table.columns)
        lines.append(f"Table {table.name}: {columns_desc}")

        for fk in table.foreign_keys:
            lines.append(
                f"  - {table.name}.{fk.column} references "
                f"{fk.references_table}.{fk.references_column}"
            )

    return "\n".join(lines)


def generate_sql(question: str, schema: SchemaResponse) -> str:
    """
    Sends the user's question and the database schema to Groq, and
    returns the generated SQL as a plain string.
    """
    schema_text = _schema_to_text(schema)

    system_prompt = (
        "You are a SQL generator. You are given a database schema and a "
        "question in plain English. Respond with ONLY a single valid SQL "
        "SELECT query that answers the question — no explanation, no "
        "markdown formatting, no code fences, just the raw SQL. "
        "Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or any "
        "statement other than SELECT. Only use tables and columns that "
        "exist in the schema provided."
    )

    table_names = [t.name for t in schema.tables]
    user_prompt = (
        f"Available tables (use ONLY these exact names, never invent a "
        f"different table name): {table_names}\n\n"
        f"Schema:\n{schema_text}\n\n"
        f"Question: {question}\n\nSQL:"
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

    # Some models wrap output in markdown code fences despite instructions
    # not to — strip those defensively.
    if sql.startswith("```"):
        sql = sql.strip("`")
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()

    return sql
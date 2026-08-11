"""
Decides whether a user's question needs an actual SQL query against
the data, or is a question about the database's structure/capabilities
that can be answered directly from the schema — then produces a
plain-English answer either way.
"""

from groq import Groq

from app.core.config import settings
from app.models.schema import SchemaResponse
from app.services.text_to_sql import _schema_to_text

client = Groq(api_key=settings.GROQ_API_KEY)


def classify_intent(question: str, schema: SchemaResponse) -> str:
    """
    Returns "meta" for questions about what's possible, what tables
    exist, or what reports could be generated — no query needed.
    Returns "data" for anything asking for actual numbers, records,
    or comparisons — requires running a query.
    """
    table_names = [t.name for t in schema.tables]
    system_prompt = (
        "You classify a user's question about a database into exactly "
        "one category. Respond with ONLY the single word 'data' or "
        "'meta' — nothing else, no punctuation.\n\n"
        "'meta' = asks what's possible, what reports could be made, "
        "what tables/columns exist, or general capability questions.\n"
        "'data' = asks for actual numbers, counts, comparisons, or "
        "specific records — requires running a query against the data."
    )
    user_prompt = f"Tables available: {table_names}\n\nQuestion: {question}\n\nCategory:"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )
    result = response.choices[0].message.content.strip().lower()
    return "meta" if "meta" in result else "data"


def answer_meta_question(question: str, schema: SchemaResponse) -> str:
    """
    Answers questions about the database's structure or capabilities
    directly from the schema, without running any SQL.
    """
    schema_text = _schema_to_text(schema)
    system_prompt = (
        "You are a helpful data assistant. Given a database schema, "
        "answer the user's question about its structure or what's "
        "possible with it. Be concise and practical. If asked what "
        "reports could be generated, suggest 4-6 concrete, specific "
        "report ideas based on the ACTUAL tables and columns given — "
        "not generic suggestions. Use a short numbered list where "
        "appropriate. Never write SQL in this answer."
    )
    user_prompt = f"Database: {schema.database}\n\nSchema:\n{schema_text}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def summarize_data_answer(question: str, columns: list, rows: list) -> str:
    """
    Turns raw query results into a short, direct, plain-English answer
    to the original question, instead of just handing back a table.
    """
    sample_rows = rows[:30]
    system_prompt = (
        "You are a helpful data assistant. Given the user's question "
        "and the actual query results, write a short, direct answer "
        "(1-3 sentences) using the real numbers and names from the "
        "data. Never mention SQL or 'the table'. If several rows are "
        "notable, a short bullet list is fine. Be concise."
    )
    user_prompt = f"Question: {question}\n\nColumns: {columns}\n\nResults:\n{sample_rows}\n\nAnswer:"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
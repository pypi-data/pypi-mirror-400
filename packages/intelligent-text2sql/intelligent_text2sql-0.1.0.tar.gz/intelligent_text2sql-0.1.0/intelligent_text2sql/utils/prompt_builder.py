def build_sql_prompt(user_query: str, schema_chunks: list) -> str:
    schema_text = "\n".join(schema_chunks[:1])


    prompt = f"""
You are a SQL expert.
Generate ONLY a valid SQLite SQL query.
DO NOT explain.
DO NOT add markdown.
DO NOT add text before or after SQL.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{user_query}

SQL QUERY:
"""
    return prompt.strip()

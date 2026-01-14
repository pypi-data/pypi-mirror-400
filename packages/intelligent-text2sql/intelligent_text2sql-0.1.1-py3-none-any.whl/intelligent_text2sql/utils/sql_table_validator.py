import re

def extract_tables_from_sql(sql: str):
    sql_upper = sql.upper()
    tables = []

    tables += re.findall(r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql_upper)
    tables += re.findall(r"JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql_upper)

    return [t.lower() for t in tables]


def validate_tables(sql: str, schema: dict):
    sql_tables = extract_tables_from_sql(sql)
    schema_tables = set(schema.keys())

    invalid_tables = [t for t in sql_tables if t not in schema_tables]

    return invalid_tables

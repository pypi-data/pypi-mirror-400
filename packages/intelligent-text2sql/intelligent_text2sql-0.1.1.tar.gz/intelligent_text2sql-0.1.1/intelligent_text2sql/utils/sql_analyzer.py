import re

def extract_tables(sql: str):
    sql_upper = sql.upper()

    from_tables = re.findall(r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql_upper)
    join_tables = re.findall(r"JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql_upper)

    return [t.lower() for t in (from_tables + join_tables)]


def extract_group_by_columns(sql: str):
    match = re.search(r"GROUP BY\s+(.+?)(ORDER BY|LIMIT|;|$)", sql, re.IGNORECASE)
    if not match:
        return []

    cols = match.group(1)
    return [c.strip() for c in cols.split(",")]

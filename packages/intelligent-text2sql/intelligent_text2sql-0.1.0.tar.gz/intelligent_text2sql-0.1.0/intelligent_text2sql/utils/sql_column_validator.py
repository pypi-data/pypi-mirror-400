import re

def extract_columns(sql: str):
    """
    Extract column references like:
    - table.column
    - column
    """
    return re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)\b", sql)


def validate_columns(sql: str, schema: dict):
    """
    Returns a list of invalid (table.column) references
    """
    invalid = []

    for ref in extract_columns(sql):
        table, column = ref.split(".")
        table = table.lower()
        column = column.lower()

        if table not in schema:
            invalid.append(ref)
        else:
            valid_cols = [c["column"].lower() for c in schema[table]]
            if column not in valid_cols:
                invalid.append(ref)

    return invalid

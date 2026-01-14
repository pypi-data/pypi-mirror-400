def resolve_group_by(sql: str, schema: dict):
    from intelligent_text2sql.utils.sql_analyzer import (
        extract_tables,
        extract_group_by_columns
    )

    tables_in_query = extract_tables(sql)
    group_cols = extract_group_by_columns(sql)

    if not group_cols:
        return sql

    resolved_cols = []

    for col in group_cols:
        # already qualified
        if "." in col:
            resolved_cols.append(col)
            continue

        # find which tables contain this column
        candidate_tables = [
            table for table, cols in schema.items()
            if col in [c["column"] for c in cols]
        ]

        # only keep tables actually used in SQL
        valid_tables = [t for t in candidate_tables if t in tables_in_query]

        if len(valid_tables) == 1:
            resolved_cols.append(f"{valid_tables[0]}.{col}")
        else:
            # cannot resolve safely → keep original
            resolved_cols.append(col)

    new_group_by = ", ".join(resolved_cols)

    import re
    sql = re.sub(
        r"GROUP BY\s+(.+?)(ORDER BY|LIMIT|;|$)",
        f"GROUP BY {new_group_by} \\2",
        sql,
        flags=re.IGNORECASE
    )

    return sql

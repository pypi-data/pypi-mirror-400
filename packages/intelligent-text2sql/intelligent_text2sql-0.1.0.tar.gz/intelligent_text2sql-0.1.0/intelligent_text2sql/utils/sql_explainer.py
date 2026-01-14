def explain_sql(sql: str) -> str:
    explanation = []

    sql_upper = sql.upper()

    if "SELECT" in sql_upper:
        explanation.append("Selects specific columns from the database.")
    if "JOIN" in sql_upper:
        explanation.append("Combines data from multiple tables.")
    if "WHERE" in sql_upper:
        explanation.append("Filters rows based on conditions.")
    if "GROUP BY" in sql_upper:
        explanation.append("Aggregates data by grouping rows.")
    if "ORDER BY" in sql_upper:
        explanation.append("Sorts the result set.")
    if "LIMIT" in sql_upper:
        explanation.append("Limits the number of results.")

    return " ".join(explanation)

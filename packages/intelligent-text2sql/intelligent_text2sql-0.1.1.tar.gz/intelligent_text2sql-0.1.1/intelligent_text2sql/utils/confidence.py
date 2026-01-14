def compute_confidence(sql: str) -> float:
    score = 1.0

    sql_upper = sql.upper()

    if "JOIN" in sql_upper:
        score -= 0.1
    if "GROUP BY" in sql_upper:
        score -= 0.1
    if "ORDER BY" in sql_upper:
        score -= 0.05
    if "WHERE" in sql_upper:
        score -= 0.05

    return max(round(score, 2), 0.5)

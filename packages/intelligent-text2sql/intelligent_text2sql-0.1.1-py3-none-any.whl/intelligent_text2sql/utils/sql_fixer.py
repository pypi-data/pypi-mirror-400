def fix_ambiguous_group_by(sql: str) -> str:
    sql_upper = sql.upper()

    # Fix common ambiguous GROUP BY customer_id
    if "GROUP BY CUSTOMER_ID" in sql_upper:
        sql = sql.replace(
            "GROUP BY customer_id",
            "GROUP BY customers.customer_id"
        )

    return sql

# import re

# def clean_sql(sql: str) -> str:
#     if not sql:
#         return sql

#     # Remove markdown code fences
#     sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
#     sql = re.sub(r"```", "", sql)

#     # Remove wrapping backticks
#     sql = sql.strip()
#     if sql.startswith("`") and sql.endswith("`"):
#         sql = sql[1:-1]

#     # Final strip
#     return sql.strip()


import re

def clean_sql(sql: str) -> str:
    if not sql:
        return sql

    # Remove markdown or backticks
    sql = sql.strip()
    sql = re.sub(r"```sql|```", "", sql, flags=re.IGNORECASE)

    # Normalize alias names: replace spaces with underscores
    # Handles: AS "Total Purchases" → AS total_purchases
    def normalize_alias(match):
        alias = match.group(1)
        alias = alias.strip().lower().replace(" ", "_")
        return f"AS {alias}"

    sql = re.sub(
        r'AS\s+"([^"]+)"',
        normalize_alias,
        sql,
        flags=re.IGNORECASE
    )

    return sql.strip()

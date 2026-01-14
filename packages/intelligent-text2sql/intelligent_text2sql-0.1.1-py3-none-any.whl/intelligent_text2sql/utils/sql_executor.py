import sqlite3
import pandas as pd

def execute_sql_safe(db_path: str, sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)

    try:
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()

    return df

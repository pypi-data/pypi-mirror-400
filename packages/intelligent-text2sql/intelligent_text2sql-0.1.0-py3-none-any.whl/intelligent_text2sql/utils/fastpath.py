def fast_sql(query: str):
    q = query.lower().strip()

    if q in ["list customers", "show customers"]:
        return "SELECT * FROM customers;"

    if q in ["list orders", "show all orders"]:
        return "SELECT * FROM orders;"

    return None

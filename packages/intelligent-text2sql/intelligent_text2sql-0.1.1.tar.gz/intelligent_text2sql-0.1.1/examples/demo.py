from intelligent_text2sql.core.engine import Text2SQL

engine = Text2SQL("sqlite:///data/sales.db")

queries = [
    "Show top customers by total purchase",
    "Show total sales per customer",
    "List customers",
    "Show all orders",
    "Show customers from Mumbai"
]

for q in queries:
    print("\nQUERY:", q)
    result = engine.run(q)
    print(result)
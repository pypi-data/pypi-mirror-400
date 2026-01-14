def schema_to_text(schema: dict) -> str:
    lines = []

    for table, columns in schema.items():
        col_desc = ", ".join(
            [f"{col['column']} ({col['type']})" for col in columns]
        )
        lines.append(f"Table {table} has columns: {col_desc}.")

    return "\n".join(lines)

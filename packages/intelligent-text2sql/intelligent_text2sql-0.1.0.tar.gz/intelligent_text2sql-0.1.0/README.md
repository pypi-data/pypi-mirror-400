 # Intelligent Text-to-SQL

A zero-cost, offline, schema-aware Text-to-SQL engine using local LLMs.

## Features
- No paid APIs
- Works offline (Ollama)
- Schema-aware SQL generation
- Handles ambiguity & hallucinations
- Safe SQL execution
- pip-installable

## Installation
```bash
pip install -e .


from intelligent_text2sql import Text2SQL

engine = Text2SQL("sqlite:///data/sales.db")
result = engine.run("Show top customers by total purchase")

print(result["sql"])
print(result["data"])
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from intelligent_text2sql.utils.db_utils import get_sqlite_schema
from intelligent_text2sql.utils.embedding_utils import embed_text
from intelligent_text2sql.utils.prompt_builder import build_sql_prompt
from intelligent_text2sql.utils.ollama_client import ask_ollama
from intelligent_text2sql.utils.sql_cleaner import clean_sql
from intelligent_text2sql.utils.sql_validator import is_safe_sql
from intelligent_text2sql.utils.sql_executor import execute_sql_safe
from intelligent_text2sql.utils.confidence import compute_confidence
from intelligent_text2sql.utils.sql_explainer import explain_sql
from intelligent_text2sql.utils.ambiguity import detect_ambiguity, build_clarification
from intelligent_text2sql.utils.sql_disambiguator import resolve_group_by
from intelligent_text2sql.utils.sql_table_validator import validate_tables
from intelligent_text2sql.utils.fastpath import fast_sql
from intelligent_text2sql.utils.sql_column_validator import validate_columns


class Text2SQL:
    def __init__(self, db_url: str, llm_backend: str | None = None):
        """
        llm_backend:
        - None        → no LLM (safe / fast-path only)
        - "ollama"    → local Ollama LLM
        """
        self.db_path = db_url.replace("sqlite:///", "")
        self.llm_backend = llm_backend

        # 1. Load schema
        self.schema = get_sqlite_schema(self.db_path)

        # 2. Build schema chunks
        self.schema_chunks = [
            f"Table {table} has columns: " +
            ", ".join([c["column"] for c in cols])
            for table, cols in self.schema.items()
        ]

        # 3. Cache schema embeddings
        self.schema_embeddings = embed_text(self.schema_chunks)

    def _get_relevant_schema(self, query, top_k=1):
        query_embedding = embed_text(query)

        similarities = cosine_similarity(
            query_embedding.reshape(1, -1),
            self.schema_embeddings
        )[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [self.schema_chunks[i] for i in top_indices]

    def run(self, query: str):
        # FAST PATH
        fast = fast_sql(query)
        if fast:
            sql = clean_sql(fast)
            df = execute_sql_safe(self.db_path, sql)
            return {
                "sql": sql,
                "data": df,
                "confidence": 0.95,
                "explanation": "Query handled using fast rule-based path."
            }


        # Ambiguity check
        ambiguities = detect_ambiguity(query)
        if ambiguities:
            return {
                "needs_clarification": True,
                "message": build_clarification(ambiguities),
                "ambiguities": ambiguities
            }

        relevant_schema = self._get_relevant_schema(query)
        prompt = build_sql_prompt(query, relevant_schema)

        if self.llm_backend != "ollama":
            return {
                "error": "LLM backend not configured",
                "confidence": 0.0,
                "explanation": (
                    "No LLM backend is configured. "
                    "Install and configure Ollama or use a supported LLM backend."
                )
            }

        raw_sql = ask_ollama(prompt, model="phi")
 #Later i have to change it to phi or low storage model
        sql = clean_sql(raw_sql)

        invalid_columns = validate_columns(sql, self.schema)

        if invalid_columns:
            return {
                "sql": sql,
                "error": f"Invalid column(s) referenced: {invalid_columns}",
                "confidence": 0.25,
                "explanation": (
                    "The generated SQL references columns not present in the database schema. "
                    "This is a known limitation of language models."
                )
            }


        sql = resolve_group_by(sql, self.schema)

        if not is_safe_sql(sql):
            raise ValueError("Unsafe SQL detected")

        invalid_tables = validate_tables(sql, self.schema)

        if invalid_tables:
            return {
                "sql": sql,
                "error": f"Unknown table(s) referenced: {invalid_tables}",
                "confidence": 0.3,
                "explanation": "The generated SQL references tables not present in the database schema."
            }

        df = execute_sql_safe(self.db_path, sql)



        return {
            "sql": sql,
            "data": df,
            "confidence": compute_confidence(sql),
            "explanation": explain_sql(sql)
        }

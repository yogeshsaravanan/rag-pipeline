"""
Central configuration loaded from environment variables.
All tuneable knobs live here so nothing is hard-coded elsewhere.
"""
import os

# ── Ollama ──────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
LLM_MODEL: str       = os.getenv("LLM_MODEL",       "llama3.2")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# ── SQLite (swap for Postgres by changing the URL) ───────────────────────────
SQLALCHEMY_DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "sqlite:///./data/production_data.db"
)

# ── ChromaDB ─────────────────────────────────────────────────────────────────
CHROMA_PERSIST_PATH: str = os.getenv("CHROMA_PERSIST_PATH", "./data/chroma_db")

# ── RAG retrieval knobs ──────────────────────────────────────────────────────
USER_CONTEXT_TOP_K:   int = int(os.getenv("USER_CONTEXT_TOP_K",   "2"))
GLOBAL_CONTEXT_TOP_K: int = int(os.getenv("GLOBAL_CONTEXT_TOP_K", "3"))

# ── Chunking knobs ───────────────────────────────────────────────────────────
SENTENCES_PER_CHUNK: int = int(os.getenv("SENTENCES_PER_CHUNK", "3"))
CHUNK_OVERLAP:       int = int(os.getenv("CHUNK_OVERLAP",       "1"))

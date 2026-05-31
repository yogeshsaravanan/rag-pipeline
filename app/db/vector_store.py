"""
ChromaDB client — single shared instance used across the whole app.
All upsert / query / delete operations on the two collections live here.
"""
import chromadb

from app.core.config import CHROMA_PERSIST_PATH

# ── Singleton client ──────────────────────────────────────────────────────────
_chroma_client: chromadb.PersistentClient | None = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
    return _chroma_client


# ── Collection helpers ────────────────────────────────────────────────────────
def get_user_collection():
    return get_chroma_client().get_or_create_collection(name="user_data_stream")


def get_knowledge_collection():
    return get_chroma_client().get_or_create_collection(name="knowledge_base")

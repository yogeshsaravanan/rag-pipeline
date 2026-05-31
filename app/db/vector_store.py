"""
ChromaDB client — single shared instance used across the whole app.

Compatibility: chromadb >= 1.0.0 (Rust rewrite), tested on 1.5.9.

Key 1.x behaviour changes accounted for here:
  - PersistentClient returns chromadb.ClientAPI, not the old Python class.
  - get_or_create_collection() with metadata on an *existing* collection now
    ignores the metadata argument silently (changed in v0.5.11).  Passing
    metadata here would be a silent no-op on re-runs, so we never pass it.
  - In 1.5.x, calling get_or_create_collection() against an existing collection
    whose stored metadata differs from the call-site metadata arg can SIGSEGV
    in the Rust bindings.  We avoid that entirely by using the
    get → (NotFoundError) → create pattern instead of get_or_create.
  - HNSW index settings are now passed via `configuration=` dict, not via
    hnsw:* metadata keys (deprecated since 1.0).  We set cosine distance
    explicitly on both collections so behaviour is predictable regardless of
    server defaults.
  - list_collections() returns Collection objects again (reverted in 1.0 from
    the v0.6 change that returned names only).
"""

from __future__ import annotations

import chromadb
from chromadb.errors import NotFoundError

from app.core.config import CHROMA_PERSIST_PATH

# ── HNSW index configuration (1.x style) ─────────────────────────────────────
# Passed only at *creation* time; ignored on subsequent gets.
# cosine is the right default for sentence/token embeddings from nomic-embed-text.
_HNSW_CONFIG = {
    "hnsw": {
        "space": "cosine",
    }
}

# ── Singleton client ──────────────────────────────────────────────────────────
_chroma_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
    return _chroma_client


# ── Safe get-or-create helper ─────────────────────────────────────────────────
def _get_or_create_collection(
    name: str,
) -> chromadb.Collection:
    """
    Safe replacement for client.get_or_create_collection().

    In chromadb 1.5.x, get_or_create_collection() can SIGSEGV when the
    call-site metadata differs from the stored collection metadata (upstream
    bug in chromadb_rust_bindings).  Splitting into an explicit get then
    create avoids touching metadata on an existing collection at all.

    The `configuration` dict is only accepted by create_collection(); passing
    it to get_collection() raises a TypeError in 1.x, so we omit it there.
    """
    client = get_chroma_client()
    try:
        return client.get_collection(name=name)
    except NotFoundError:
        return client.create_collection(
            name=name,
            configuration=_HNSW_CONFIG,
        )


# ── Collection helpers ────────────────────────────────────────────────────────
def get_user_collection() -> chromadb.Collection:
    """
    Volatile user transaction stream (per-user order history).
    Queried with a where={"user_id": ...} filter at runtime.
    """
    return _get_or_create_collection("user_data_stream")


def get_knowledge_collection() -> chromadb.Collection:
    """
    Global document knowledge base (uploaded .txt / .docx chunks).
    Queried without a user filter.
    """
    return _get_or_create_collection("knowledge_base")
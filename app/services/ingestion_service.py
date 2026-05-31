"""
Document ingestion pipeline.

Accepts raw text (already extracted from .txt / .docx by the API layer),
chunks it by sentences, embeds each chunk, and upserts into the
knowledge_base ChromaDB collection.
"""
import re
from typing import List

from app.core.config import SENTENCES_PER_CHUNK, CHUNK_OVERLAP
from app.db.vector_store import get_knowledge_collection
from app.services.ollama_service import get_embedding


# ── Text chunking ─────────────────────────────────────────────────────────────
def chunk_text_by_sentences(
    text: str,
    sentences_per_chunk: int = SENTENCES_PER_CHUNK,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Splits text into overlapping sentence-based windows.
    Keeps tight semantic context rather than arbitrary word counts.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks: List[str] = []
    i = 0
    while i < len(sentences):
        window     = sentences[i : i + sentences_per_chunk]
        chunks.append(" ".join(window))
        i += sentences_per_chunk - overlap
        if i >= len(sentences) or len(window) < sentences_per_chunk:
            break

    return chunks


# ── Ingest pipeline ───────────────────────────────────────────────────────────
def ingest_document(filename: str, raw_text: str) -> int:
    """
    Chunk → embed → upsert the document into the knowledge_base collection.
    Returns the number of chunks stored.
    """
    chunks     = chunk_text_by_sentences(raw_text)
    collection = get_knowledge_collection()

    for idx, chunk in enumerate(chunks):
        chunk_id = f"doc_{filename}_{idx}"
        vector   = get_embedding(chunk)
        collection.upsert(
            ids        = [chunk_id],
            embeddings = [vector],
            documents  = [chunk],
            metadatas  = [{"source_file": filename, "type": "global_knowledge"}],
        )

    return len(chunks)

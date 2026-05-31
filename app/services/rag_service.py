"""
Live RAG query pipeline.

Steps
  1. Rewrite the user query into optimised search terms.
  2. Embed the rewritten query.
  3. Retrieve top-K records from user_data_stream (per user_id).
  4. Retrieve top-K chunks from knowledge_base (global).
  5. Generate a grounded answer from the combined context.
"""
from typing import Dict, Any

from app.core.config import USER_CONTEXT_TOP_K, GLOBAL_CONTEXT_TOP_K
from app.db.vector_store import get_user_collection, get_knowledge_collection
from app.services.ollama_service import get_embedding, chat_completion

# ── System prompts ────────────────────────────────────────────────────────────
_REWRITE_SYSTEM = (
    "You are a search query optimizer. "
    "Rewrite the user's input into key search terms for an internal database lookup. "
    "Return ONLY the optimized search terms, nothing else."
)

_GENERATE_SYSTEM = (
    "CRITICAL RULE: Answer the user's query using ONLY the explicitly stated facts "
    "in the provided Context block. "
    "If the Context block does not explicitly state the answer, you MUST respond with: "
    "'I do not have access to that information in our current records.' "
    "DO NOT use your pre-trained background knowledge or make up steps."
)


# ── Public pipeline entry-point ───────────────────────────────────────────────
def run_rag_pipeline(user_id: int, query: str) -> Dict[str, Any]:
    # 1. Rewrite query
    optimised_query = chat_completion(query, _REWRITE_SYSTEM)
    print(f"[RAG] Optimised query: {optimised_query}")

    # 2. Embed
    query_vector = get_embedding(optimised_query)

    # 3. User-scoped retrieval
    user_results = get_user_collection().query(
        query_embeddings=[query_vector],
        n_results=USER_CONTEXT_TOP_K,
        where={"user_id": user_id},
    )
    user_context = user_results.get("documents", [[]])[0]
    print(f"[RAG] User context chunks: {len(user_context)}")

    # 4. Global knowledge-base retrieval
    doc_results = get_knowledge_collection().query(
        query_embeddings=[query_vector],
        n_results=GLOBAL_CONTEXT_TOP_K,
    )
    doc_context = doc_results.get("documents", [[]])[0]
    print(f"[RAG] Knowledge-base chunks: {len(doc_context)}")

    # 5. Generate
    combined = user_context + doc_context
    if not combined:
        return {
            "user_id": user_id,
            "response": "I couldn't find any account details or documents matching your request.",
            "sources_used": {"user_order_records_found": 0, "knowledge_base_chunks_found": 0},
        }

    context_block = "\n".join(f"- {c}" for c in combined)
    prompt        = f"Context:\n{context_block}\n\nUser Question: {query}"
    answer        = chat_completion(prompt, _GENERATE_SYSTEM)
    print(f"[RAG] Answer generated.")

    return {
        "user_id": user_id,
        "response": answer,
        "sources_used": {
            "user_order_records_found":    len(user_context),
            "knowledge_base_chunks_found": len(doc_context),
        },
    }

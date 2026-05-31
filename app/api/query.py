"""
RAG pipeline query endpoint.
"""
from fastapi import APIRouter

from app.api.schemas import QueryRequest
from app.services.rag_service import run_rag_pipeline

router = APIRouter(prefix="/api/v1", tags=["RAG Query"])


@router.post("/query")
def query(payload: QueryRequest):
    """Execute the dual-stream RAG pipeline for a given user and question."""
    return run_rag_pipeline(user_id=payload.user_id, query=payload.query)

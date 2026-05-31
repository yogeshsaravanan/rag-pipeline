"""
Pydantic models used by the API layer for request validation and
response serialisation.
"""
from pydantic import BaseModel, Field


# ── Orders ────────────────────────────────────────────────────────────────────
class OrderCreate(BaseModel):
    user_id:      int   = Field(..., gt=0, description="Owning user's ID")
    product_name: str   = Field(..., min_length=1)
    details:      str   = Field(default="")


class OrderResponse(BaseModel):
    id:     int
    status: str


# ── RAG query ─────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    user_id: int  = Field(..., gt=0)
    query:   str  = Field(..., min_length=1)

"""
Application factory.

Import order matters here: cdc_service must be imported before the
first DB session so that SQLAlchemy ORM event hooks are registered.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

# Register CDC hooks (side-effect import — must come before DB init)
import app.services.cdc_service  # noqa: F401

from app.db.database import init_db
from app.api import documents, orders, query


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Run startup tasks before serving requests."""
    init_db()
    yield


app = FastAPI(
    title="Dual-Stream RAG Pipeline",
    description="Production RAG service with SQLite CDC → ChromaDB and Ollama LLM.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(orders.router)
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

"""
All communication with the local Ollama instance.

Two public helpers:
  • get_embedding(text)        → List[float]
  • chat_completion(prompt, system_prompt) → str
"""
from typing import List

import requests
from fastapi import HTTPException

from app.core.config import OLLAMA_BASE_URL, EMBEDDING_MODEL, LLM_MODEL


# ── Embedding ─────────────────────────────────────────────────────────────────
def get_embedding(text: str) -> List[float]:
    """
    Calls /api/embed and returns the first embedding vector.
    Raises HTTP 500 if Ollama is unreachable or returns an error.
    """
    payload = {"model": EMBEDDING_MODEL, "input": text}
    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/embed", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["embeddings"][0]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama embedding error: {exc}",
        )


# ── Chat / generation ─────────────────────────────────────────────────────────
def chat_completion(prompt: str, system_prompt: str = "") -> str:
    """
    Sends a single-turn chat request to /api/chat and returns the
    assistant message content as a plain string.
    """
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.0},
    }
    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama chat error: {exc}",
        )

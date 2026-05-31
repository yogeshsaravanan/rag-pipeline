# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps needed to compile some wheels (e.g. chromadb's hnswlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy pre-built packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/

# Persistent data lives on a volume; pre-create the directory
RUN mkdir -p /app/data/chroma_db

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser \
 && chown -R appuser /app
USER appuser

EXPOSE 8000

# Use a single worker for SQLite safety; switch to gunicorn + workers for Postgres
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

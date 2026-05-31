"""
Document upload endpoint.
Accepts .txt and .docx files, extracts text, and delegates to the
ingestion service for chunking + vector storage.
"""
import io

import docx
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ingestion_service import ingest_document

router = APIRouter(prefix="/api/v1", tags=["Documents"])


@router.post("/upload-doc")
async def upload_document(filename: str, file: UploadFile = File(...)):
    """
    Upload a .txt or .docx file into the global knowledge base.
    The filename query-parameter determines how chunk IDs are generated.
    """
    contents = await file.read()
    raw_text = ""

    if filename.endswith(".docx"):
        try:
            doc      = docx.Document(io.BytesIO(contents))
            raw_text = "\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to parse .docx: {exc}")

    elif filename.endswith(".txt"):
        try:
            raw_text = contents.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = contents.decode("windows-1252")

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Upload a .txt or .docx file.",
        )

    chunks_stored = ingest_document(filename, raw_text)

    return {
        "status":           "success",
        "chunks_processed": chunks_stored,
        "target_collection": "knowledge_base",
    }

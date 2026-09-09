"""
Handles the /ingest endpoint: accepts an uploaded PDF, chunks it,
embeds it, and stores it in Pinecone. This is the entry point that
gets your documents INTO the system before any question can be
answered from them.
"""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.chunking import chunk_pdf
from app.services.vectorstore import add_chunks, index_stats, clear_all_vectors
from app.models.schemas import IngestResponse

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file upload, processes it, and stores it in Pinecone.

    UploadFile = File(...) tells FastAPI: expect this as multipart
    form-data (a real file upload), not JSON. The "..." means this
    field is required -- a request with no file attached gets
    automatically rejected before this function even runs.
    """

    # Basic validation: only accept PDFs. Fail early with a clear
    # error rather than letting pypdf crash confusingly later.
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    save_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file to disk. shutil.copyfileobj streams it
    # in chunks rather than loading the whole file into memory at once --
    # matters if someone uploads a large PDF.
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Run the actual pipeline: PDF -> chunks -> embed + store in Pinecone.
    try:
        chunks = chunk_pdf(save_path, file.filename)
        add_chunks(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    stats = index_stats()

    return IngestResponse(
        filename=file.filename,
        chunks_added=len(chunks),
        total_vectors_in_store=stats["total_vectors"],
    )

@router.delete("/reset")
async def reset_knowledge_base():
    """
    Wipes all stored documents. Call this before uploading a new PDF
    if you want DocSpider to only know about that one document,
    rather than accumulating a multi-document knowledge base.
    """
    clear_all_vectors()
    return {"message": "Knowledge base cleared."}
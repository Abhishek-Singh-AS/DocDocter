"""
Handles the /chat endpoint: takes a user's question, runs it through
the RAG pipeline (retrieve + generate), and returns a grounded answer
with source citations.
"""

from fastapi import APIRouter, HTTPException

from app.services.rag_chain import answer_question
from app.models.schemas import ChatRequest, ChatResponse, SourceChunk

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    request.question and request.top_k arrive already validated by
    Pydantic (from ChatRequest in schemas.py) -- if the caller sends
    malformed JSON or forgets "question", FastAPI rejects it before
    this function even runs.
    """
    try:
        result = answer_question(request.question, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")

    source_chunks = [
        SourceChunk(
            text=c["text"],
            source=c["source"],
            page=c["page"],
            score=c["score"],
        )
        for c in result["chunks"]
    ]

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        chunks=source_chunks,
    )
"""
Handles the /evaluate endpoint: runs the full test set through the
RAG pipeline, scores every answer, and returns a summary plus
per-question results.
"""

from fastapi import APIRouter, HTTPException

from app.services.evaluation import run_evaluation, run_live_evaluation
from app.models.schemas import (
    EvaluationSummary, EvaluationResult,
    LiveEvaluationRequest, LiveEvaluationSummary, LiveEvaluationResult,
)

router = APIRouter()


@router.post("/evaluate/live", response_model=LiveEvaluationSummary)
async def evaluate_live(request: LiveEvaluationRequest):
    """
    Evaluates REAL question/answer pairs from the current chat session
    against the context that was actually retrieved for each one --
    no pre-written expected answers needed. Works for any document.
    """
    qa_pairs = [
        {
            "question": pair.question,
            "answer": pair.answer,
            "chunks": [c.model_dump() for c in pair.chunks],
        }
        for pair in request.qa_pairs
    ]

    if not qa_pairs:
        raise HTTPException(status_code=400, detail="No questions to evaluate yet — ask something in the Ask tab first.")

    try:
        df = run_live_evaluation(qa_pairs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live evaluation failed: {str(e)}")

    results = [
        LiveEvaluationResult(
            question=row["question"],
            actual_answer=row["actual_answer"],
            had_context=row["had_context"],
            faithfulness=row["faithfulness"],
            relevance=row["relevance"],
            judge_reasoning=row["judge_reasoning"],
        )
        for _, row in df.iterrows()
    ]

    return LiveEvaluationSummary(
        num_questions=len(df),
        avg_faithfulness=round(df["faithfulness"].dropna().mean(), 2) if df["faithfulness"].notna().any() else None,
        avg_relevance=round(df["relevance"].dropna().mean(), 2) if df["relevance"].notna().any() else None,
        results=results,
    )
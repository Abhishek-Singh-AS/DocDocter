"""
Evaluation layer -- the part most RAG tutorials skip.

Two modes are supported:
1. File-based (run_evaluation): uses a fixed test_questions.json with
   hand-written expected answers. Good for a document you know in
   advance and want to test repeatedly over time.
2. Live (run_live_evaluation): reference-free -- judges real
   question/answer/context triples from an actual chat session,
   with no pre-written answer key needed. Works for ANY uploaded
   document, which is what a real multi-user product needs.

Every run gets logged to a CSV, so you can track how changes to
chunk_size/overlap/top_k affect real scores over time.
"""

import json
import os
import re
import pandas as pd
from datetime import datetime

from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY, LLM_MODEL
from app.services.rag_chain import answer_question

LOG_PATH = "eval/run_log.csv"

JUDGE_PROMPT_TEMPLATE = """You are grading an AI-generated answer against a reference answer.

Question: {question}
Reference (expected) answer: {expected_answer}
AI-generated answer: {actual_answer}

Score the AI answer on two dimensions, each from 1 (very poor) to 5 (excellent):
- faithfulness: is the AI answer factually consistent with the reference, with no invented details?
- relevance: does the AI answer appropriately respond to the question, GIVEN the reference answer?
  Note: if the reference answer indicates the question cannot be answered from the documents
  (e.g. "I don't have enough information..."), then an AI answer that also correctly declines
  to answer should score HIGH on relevance, not low -- refusing is the correct, relevant behavior
  in that case.

Respond with ONLY a JSON object, no other text, in this exact format:
{{"faithfulness": <int 1-5>, "relevance": <int 1-5>, "reasoning": "<one short sentence>"}}
"""


def load_test_set(path: str = "eval/test_questions.json") -> list[dict]:
    with open(path, "r") as f:
        return json.load(f)


def retrieval_hit(retrieved_chunks: list[dict], expected_keywords: list[str]):
    """
    Did at least one retrieved chunk contain at least one expected
    keyword (case-insensitive)? Returns None (not applicable) if the
    question has no keywords defined.
    """
    if not expected_keywords:
        return None

    combined_text = " ".join(c["text"].lower() for c in retrieved_chunks)
    return any(kw.lower() in combined_text for kw in expected_keywords)


def judge_answer(question: str, expected_answer: str, actual_answer: str) -> dict:
    """
    File-based judge: compares the AI's answer to a hand-written
    reference answer. Used by run_evaluation().
    """
    llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL, temperature=0)

    prompt = JUDGE_PROMPT_TEMPLATE.format(
        question=question, expected_answer=expected_answer, actual_answer=actual_answer
    )
    response = llm.invoke([("user", prompt)])
    raw = response.content

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"faithfulness": None, "relevance": None, "reasoning": "parse_failed"}

    try:
        parsed = json.loads(match.group(0))
        return {
            "faithfulness": parsed.get("faithfulness"),
            "relevance": parsed.get("relevance"),
            "reasoning": parsed.get("reasoning", ""),
        }
    except json.JSONDecodeError:
        return {"faithfulness": None, "relevance": None, "reasoning": "parse_failed"}


def run_evaluation(top_k: int = 4, test_set_path: str = "eval/test_questions.json") -> pd.DataFrame:
    """
    Runs every question in the fixed test set through the full RAG
    pipeline, scores each answer against its hand-written expected
    answer, and logs a run summary to CSV.
    """
    test_set = load_test_set(test_set_path)
    rows = []

    for item in test_set:
        question = item["question"]
        expected_answer = item["expected_answer"]
        expected_keywords = item.get("expected_keywords", [])

        result = answer_question(question, top_k=top_k)
        hit = retrieval_hit(result["chunks"], expected_keywords)
        judged = judge_answer(question, expected_answer, result["answer"])

        rows.append({
            "question": question,
            "expected_answer": expected_answer,
            "actual_answer": result["answer"],
            "sources": ", ".join(result["sources"]),
            "retrieval_hit": hit,
            "faithfulness": judged["faithfulness"],
            "relevance": judged["relevance"],
            "judge_reasoning": judged["reasoning"],
        })

    df = pd.DataFrame(rows)
    _log_run_summary(df, top_k)
    return df


def _log_run_summary(df: pd.DataFrame, top_k: int):
    """Appends one summary row per file-based evaluation run."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    applicable_hits = df["retrieval_hit"].dropna()
    hit_rate = applicable_hits.mean() if len(applicable_hits) else None

    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "file",
        "top_k": top_k,
        "num_questions": len(df),
        "retrieval_hit_rate": round(hit_rate, 3) if hit_rate is not None else None,
        "avg_faithfulness": round(df["faithfulness"].dropna().mean(), 2) if df["faithfulness"].notna().any() else None,
        "avg_relevance": round(df["relevance"].dropna().mean(), 2) if df["relevance"].notna().any() else None,
    }

    summary_df = pd.DataFrame([summary])
    if os.path.exists(LOG_PATH):
        summary_df.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        summary_df.to_csv(LOG_PATH, mode="w", header=True, index=False)


def judge_live_answer(question: str, context_chunks: list[dict], actual_answer: str) -> dict:
    """
    Reference-free judge: scores an answer using ONLY the question and
    the context it was actually retrieved from -- no hand-written
    "expected answer" needed. Used by run_live_evaluation().
    """
    llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL, temperature=0)

    context_text = "\n\n".join(c["text"] for c in context_chunks) if context_chunks else "(no context was retrieved)"

    prompt = f"""You are evaluating an AI answer for a document Q&A system.

Question: {question}

Context the AI was given (retrieved from the user's document):
{context_text}

AI's answer: {actual_answer}

Score the answer on two dimensions, 1 (very poor) to 5 (excellent):
- faithfulness: is every claim in the answer actually supported by the context above?
  If the context doesn't contain the answer AND the AI correctly said it doesn't have
  enough information, that is CORRECT behavior -- score faithfulness 5 in that case.
  Only score low if the AI invented facts not present in the context.
- relevance: does the answer directly address the question asked?

Respond with ONLY a JSON object, no other text:
{{"faithfulness": <int 1-5>, "relevance": <int 1-5>, "reasoning": "<one short sentence>"}}
"""

    response = llm.invoke([("user", prompt)])
    raw = response.content

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"faithfulness": None, "relevance": None, "reasoning": "parse_failed"}

    try:
        parsed = json.loads(match.group(0))
        return {
            "faithfulness": parsed.get("faithfulness"),
            "relevance": parsed.get("relevance"),
            "reasoning": parsed.get("reasoning", ""),
        }
    except json.JSONDecodeError:
        return {"faithfulness": None, "relevance": None, "reasoning": "parse_failed"}


def run_live_evaluation(qa_pairs: list[dict]) -> pd.DataFrame:
    """
    Evaluates a list of REAL question/answer/chunks from the current
    chat session -- not a fixed file. Each item in qa_pairs looks like:
      {"question": "...", "answer": "...", "chunks": [{"text": "...", ...}, ...]}
    """
    rows = []

    for pair in qa_pairs:
        chunks = pair.get("chunks", [])
        judged = judge_live_answer(pair["question"], chunks, pair["answer"])

        rows.append({
            "question": pair["question"],
            "actual_answer": pair["answer"],
            "had_context": len(chunks) > 0,
            "faithfulness": judged["faithfulness"],
            "relevance": judged["relevance"],
            "judge_reasoning": judged["reasoning"],
        })

    df = pd.DataFrame(rows)
    _log_live_run_summary(df)
    return df


def _log_live_run_summary(df: pd.DataFrame):
    """Same iteration-history logging as before, adapted for live runs."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "live",
        "num_questions": len(df),
        "avg_faithfulness": round(df["faithfulness"].dropna().mean(), 2) if df["faithfulness"].notna().any() else None,
        "avg_relevance": round(df["relevance"].dropna().mean(), 2) if df["relevance"].notna().any() else None,
    }

    summary_df = pd.DataFrame([summary])
    if os.path.exists(LOG_PATH):
        summary_df.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        summary_df.to_csv(LOG_PATH, mode="w", header=True, index=False)
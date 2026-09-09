"""
Pydantic models define the exact shape of data flowing in and out
of each API endpoint.
"""

from pydantic import BaseModel


# ---------- /ingest ----------

class IngestResponse(BaseModel):
    filename: str
    chunks_added: int
    total_vectors_in_store: int


# ---------- /chat ----------

class ChatRequest(BaseModel):
    question: str
    top_k: int = 4


class SourceChunk(BaseModel):
    text: str
    source: str
    page: int | str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks: list[SourceChunk]


# ---------- /evaluate ----------

class EvaluationResult(BaseModel):
    question: str
    expected_answer: str
    actual_answer: str
    sources: str
    retrieval_hit: bool | None
    faithfulness: int | None
    relevance: int | None
    judge_reasoning: str


class EvaluationSummary(BaseModel):
    num_questions: int
    retrieval_hit_rate: float | None
    avg_faithfulness: float | None
    avg_relevance: float | None
    results: list[EvaluationResult]


# ---------- /evaluate/live ----------

class LiveChunk(BaseModel):
    text: str
    source: str
    page: int | str


class LiveQAPair(BaseModel):
    question: str
    answer: str
    chunks: list[LiveChunk] = []


class LiveEvaluationRequest(BaseModel):
    qa_pairs: list[LiveQAPair]


class LiveEvaluationResult(BaseModel):
    question: str
    actual_answer: str
    had_context: bool
    faithfulness: int | None
    relevance: int | None
    judge_reasoning: str


class LiveEvaluationSummary(BaseModel):
    num_questions: int
    avg_faithfulness: float | None
    avg_relevance: float | None
    results: list[LiveEvaluationResult]
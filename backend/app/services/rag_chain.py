"""
The core RAG logic: retrieve relevant chunks for a question, build a
prompt that forces the LLM to answer ONLY from those chunks, and call
Groq to generate the answer.

This deliberately does NOT use LangChain's higher-level chain
abstractions (like RetrievalQA) -- writing the steps out explicitly
here makes it much easier to see exactly what's happening, which
matters most while you're learning. You can refactor to LCEL chains
later once this is comfortable.
"""

from langchain_groq import ChatGroq
from app.config import GROQ_API_KEY, LLM_MODEL, DEFAULT_TOP_K
from app.services.vectorstore import similarity_search

SYSTEM_PROMPT = """You are a careful assistant that answers questions using ONLY \
the provided context excerpts. Follow these rules strictly:
1. If the answer is not contained in the context, say "I don't have enough \
information in the documents to answer that." Do not guess or use outside knowledge.
2. Keep answers concise and directly grounded in the context.
3. When useful, mention which source/page the information came from.
"""


def _get_llm():
    """
    Returns a LangChain-wrapped connection to Groq's hosted LLM.
    temperature=0.1 keeps answers focused and consistent rather than
    creative -- you want a RAG system to be reliable, not imaginative.
    """
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0.1,
    )


def _build_context_block(chunks: list[dict]) -> str:
    """
    Turns the list of retrieved chunk dicts into one readable text
    block to hand the LLM, clearly labeling each excerpt's source
    so the LLM can cite it if useful.
    """
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(
            f"[Excerpt {i} | source: {chunk['source']}, page: {chunk['page']}]\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(parts)


def answer_question(question: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """
    Full RAG pipeline for one question:
      1. Retrieve top_k relevant chunks from Pinecone
      2. Build a context block from them
      3. Ask Groq's LLM to answer using ONLY that context
      4. Return the answer plus the sources used (for transparency)
    """
    chunks = similarity_search(question, top_k=top_k)

    if not chunks:
        return {
            "answer": "No documents have been ingested yet -- upload a PDF first.",
            "sources": [],
            "chunks": [],
        }

    context_block = _build_context_block(chunks)
    user_prompt = f"Context:\n{context_block}\n\nQuestion: {question}\n\nAnswer:"

    llm = _get_llm()
    response = llm.invoke([
        ("system", SYSTEM_PROMPT),
        ("user", user_prompt),
    ])

    sources = sorted({f"{c['source']} (p.{c['page']})" for c in chunks})

    return {
        "answer": response.content,
        "sources": sources,
        "chunks": chunks,
    }
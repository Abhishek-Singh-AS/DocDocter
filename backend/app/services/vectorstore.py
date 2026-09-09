"""
Wraps Pinecone as the vector store, using LangChain's PineconeVectorStore
so the rest of the app never talks to Pinecone's raw SDK directly.

Two operations happen here:
  - add_chunks(): embed + upload text chunks into the Pinecone index
  - similarity_search(): embed a question, ask Pinecone for the
    most similar stored chunks
"""

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from app.services.embeddings import get_embedding_model


def _get_vectorstore():
    """
    Connects to your existing Pinecone index (created manually in
    Task 7) and wraps it with LangChain's interface. We don't create
    the index here -- that's a one-time setup step, not something
    the app should do on every run.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    embedding_model = get_embedding_model()

    return PineconeVectorStore(index=index, embedding=embedding_model)


def add_chunks(chunks: list[dict]):
    """
    Takes a list of chunk dicts, each shaped like:
      {"id": "...", "text": "...", "source": "...", "page": 1}
    Embeds each chunk's text and uploads it to Pinecone, tagging it
    with metadata (source filename + page number) so we can show
    users where an answer came from later.
    """
    if not chunks:
        return

    vectorstore = _get_vectorstore()

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [{"source": c["source"], "page": c["page"]} for c in chunks]

    # This single call does the embedding AND the upload to Pinecone.
    vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)


def similarity_search(question: str, top_k: int = 4):
    """
    Embeds the question and returns the top_k most similar chunks
    from Pinecone, each as a dict with text + source metadata.
    """
    vectorstore = _get_vectorstore()

    # similarity_search_with_score also returns how close each match is --
    # useful later for debugging retrieval quality.
    results = vectorstore.similarity_search_with_score(question, k=top_k)

    output = []
    for doc, score in results:
        output.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "page": int(doc.metadata.get("page", 0)) if doc.metadata.get("page") else "?",
            "score": score,
        })
    return output


def index_stats():
    """Returns how many vectors are currently stored -- useful for the UI."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    stats = index.describe_index_stats()
    return {"total_vectors": stats.get("total_vector_count", 0)}

def clear_all_vectors():
    """
    Deletes every vector currently stored in the Pinecone index.
    Used when the user wants to start fresh with a new document
    instead of building a multi-document knowledge base.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    index.delete(delete_all=True)
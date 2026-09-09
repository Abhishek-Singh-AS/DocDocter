"""
Wraps the embedding model. This runs the embedding model LOCALLY
(via sentence-transformers, downloaded once and cached), rather than
calling Hugging Face's hosted API -- this avoids a known compatibility
bug in the hosted-endpoint code path, and is genuinely lightweight:
bge-small is ~130MB and runs fast on CPU even on modest hardware.

Every other file that needs to turn text into vectors imports
get_embedding_model() from here.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from app.config import EMBEDDING_MODEL


def get_embedding_model():
    """
    Returns a LangChain embedding object that runs bge-small locally
    on CPU. Has two key methods used elsewhere in the project:
      - .embed_documents(list_of_texts) -> list of vectors (storing chunks)
      - .embed_query(single_text)       -> one vector (a user's question)

    The first time this runs, it downloads the model weights (~130MB)
    and caches them on disk -- subsequent runs are instant.
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
"""
Central configuration for the whole backend.
Every other file imports settings from here instead of reading
os.environ directly -- so if a key name or model changes, you only
update it in this one file.
"""

import os
from dotenv import load_dotenv

# Reads the .env file in your backend folder and loads its values
# into the environment, so os.getenv() below can find them.
load_dotenv()

# --- API Keys (pulled from your .env file) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# --- Model names (open-source models served via Groq / Hugging Face) ---
LLM_MODEL = "openai/gpt-oss-20b"       # Groq's current recommended fast free model (replaces the deprecated llama-3.1-8b-instant)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # small, fast, well-regarded open embedding model

# --- Pinecone settings ---
PINECONE_INDEX_NAME = "rag-project-index"
EMBEDDING_DIMENSION = 384   # bge-small outputs 384-dimensional vectors -- must match when creating the Pinecone index

# --- Chunking defaults ---
CHUNK_SIZE = 800     # characters per chunk
CHUNK_OVERLAP = 150  # overlap between chunks, to avoid cutting ideas in half

# --- Retrieval defaults ---
DEFAULT_TOP_K = 4    # how many chunks to retrieve per question

# --- Safety check: fail loudly and early if a key is missing ---
# This runs the moment config.py is imported anywhere in the app.
# Better to crash here with a clear message than get a confusing
# error later deep inside a Groq or Pinecone API call.
def _check_keys():
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not HF_API_TOKEN:
        missing.append("HF_API_TOKEN")
    if not PINECONE_API_KEY:
        missing.append("PINECONE_API_KEY")

    if missing:
        raise RuntimeError(
            f"Missing required keys in .env: {', '.join(missing)}. "
            f"Check that backend/.env exists and contains these values."
        )

_check_keys()
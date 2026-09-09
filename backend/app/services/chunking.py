"""
Extracts text from a PDF and splits it into overlapping chunks.
Uses LangChain's RecursiveCharacterTextSplitter, which tries to
split on paragraph breaks first, then sentences, then words --
only falling back to a hard character cut as a last resort. This
produces cleaner chunks than a naive fixed-length slice.
"""

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_by_page(pdf_path: str) -> list[tuple[int, str]]:
    """
    Reads a PDF and returns a list of (page_number, text) tuples.
    Skips pages with no extractable text (e.g. pure image/scanned pages).
    """
    reader = PdfReader(pdf_path)
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = " ".join(text.split())  # collapse messy whitespace/line breaks
        if text.strip():
            pages.append((i + 1, text))

    return pages


def chunk_pdf(pdf_path: str, source_name: str) -> list[dict]:
    """
    Full pipeline: PDF -> pages -> chunks.
    Returns a list of dicts shaped exactly how vectorstore.add_chunks()
    expects:
      {"id": "...", "text": "...", "source": "...", "page": 1}
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],  # tries these in order
    )

    pages = extract_text_by_page(pdf_path)
    all_chunks = []
    chunk_counter = 0

    for page_num, page_text in pages:
        page_chunks = splitter.split_text(page_text)
        for chunk_text in page_chunks:
            chunk_counter += 1
            all_chunks.append({
                "id": f"{source_name}_p{page_num}_c{chunk_counter}",
                "text": chunk_text,
                "source": source_name,
                "page": page_num,
            })

    return all_chunks
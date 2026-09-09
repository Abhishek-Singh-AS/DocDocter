# 🕸️ DocSpider

Upload a PDF, ask it questions, and get answers backed only by that document — with a built-in quality checker that scores how trustworthy each answer actually is.

## What it does

1. **Upload** — drop in a PDF, it gets split into chunks and stored
2. **Ask** — ask questions, get answers with source citations (page numbers included)
3. **Quality Check** — automatically grades your real questions/answers for accuracy — works on any document, no manual setup needed

If the answer isn't in the document, DocSpider says so instead of guessing.

## How it works

PDF Upload → Split into chunks → Convert to embeddings → Store in Pinecone

Question asked → Find matching chunks → Groq LLM answers using only those chunks → Answer + sources shown

Quality Check → LLM judges each real answer against what was actually retrieved → Faithfulness + Relevance scores


## Tech stack

| Part | Tool |
|---|---|
| Backend | FastAPI + LangChain |
| LLM | Groq (`openai/gpt-oss-20b`) — free, open-source model |
| Embeddings | `BAAI/bge-small-en-v1.5` — runs locally, no API cost |
| Vector database | Pinecone (free tier) |
| Frontend | React + Vite |
| Hosting | Render (backend) + Vercel (frontend) — both free |

100% free stack — no paid APIs, no GPU needed.

## Project structure

rag-web-app/
├── backend/
│ ├── app/
│ │ ├── main.py → starts the app
│ │ ├── config.py → API keys & settings
│ │ ├── routers/ → /ingest, /chat, /evaluate endpoints
│ │ ├── services/ → chunking, embeddings, vector search, LLM logic
│ │ └── models/ → request/response formats
│ └── requirements.txt
│
└── frontend/
└── src/
├── App.jsx → main layout
├── api/client.js → talks to the backend
└── components/ → Upload, Chat, Quality Check screens


## Run it locally

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file with:
GROQ_API_KEY=your_key
HF_API_TOKEN=your_key
PINECONE_API_KEY=your_key

Then:
```bash
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs`

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`

## Live demo

🔗 [Add link here once deployed]

## What I learned

- Chunking size/overlap directly affects answer quality
- LLM-as-judge evaluation works without a pre-written answer key by grading answers against their own retrieved context
- Python AI packages break often — pinning exact versions in `requirements.txt` avoids dependency conflicts
- A good RAG system should say "I don't know" rather than guess
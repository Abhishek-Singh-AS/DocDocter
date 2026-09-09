"""
FastAPI application entrypoint. This file's only job is to create
the app, configure CORS, and mount each router -- it should stay thin.
All real logic lives in routers/ and services/.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ingest, chat, evaluate

app = FastAPI(title="DocSpider API")

# CORS: allows your React frontend (running on a different port/origin)
# to actually call this API from the browser. Without this, the browser
# blocks every request before it even reaches your endpoints.
allow_origins=[
        "http://localhost:5173",
        "https://*.vercel.app",  # placeholder -- we'll replace with your exact Vercel URL once deployed
    ],


@app.get("/")
def read_root():
    return {"message": "Backend is alive!"}


app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(evaluate.router)
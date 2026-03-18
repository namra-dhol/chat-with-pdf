"""
main.py
-------
FastAPI application entrypoint.
Defines all API routes: /health, /upload-pdf, /chat
"""

import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdf_processor import extract_text_from_pdf, split_into_chunks
from embedding_model import get_embedding, get_embeddings
from vector_store import save_store, load_store, search, DEFAULT_PKL_PATH
from chat_engine import get_answer

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Chat with PDF API",
    description="Upload a PDF and ask questions about its content using RAG.",
    version="1.0.0",
)

# Allow frontend origins (local dev + Vercel production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://chat-with-pdf-taupe-delta.vercel.app",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


class UploadResponse(BaseModel):
    message: str
    chunks_count: int
    filename: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", summary="Health check")
def health_check():
    """Simple health-check endpoint to verify the API is running."""
    return {"status": "ok", "message": "Chat with PDF API is running."}


@app.post("/upload-pdf", response_model=UploadResponse, summary="Upload and process a PDF")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accept a PDF file, extract its text, generate embeddings,
    and persist everything to my_data.pkl.
    """
    # --- Validate file type ---
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # --- Read file bytes ---
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")

    # --- Extract text from PDF ---
    try:
        full_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {e}")

    # --- Split into chunks ---
    chunks = split_into_chunks(full_text, chunk_size=500, overlap=50)
    if not chunks:
        raise HTTPException(status_code=422, detail="PDF text could not be split into chunks.")

    print(f"[Upload] '{file.filename}' → {len(chunks)} chunks.")

    # --- Generate embeddings ---
    try:
        embeddings = get_embeddings(chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {e}")

    # --- Save to pickle ---
    try:
        save_store(chunks, embeddings, DEFAULT_PKL_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data store: {e}")

    return UploadResponse(
        message=f"PDF '{file.filename}' processed and stored successfully.",
        chunks_count=len(chunks),
        filename=file.filename,
    )


@app.post("/chat", response_model=ChatResponse, summary="Ask a question about the uploaded PDF")
async def chat(request: ChatRequest):
    """
    Accept a question, search the stored embeddings for relevant context,
    and return an answer from the LLM.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # --- Load the pickle store ---
    try:
        store = load_store(DEFAULT_PKL_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data store: {e}")

    # --- Embed the user question ---
    try:
        query_embedding = get_embedding(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to embed question: {e}")

    # --- Retrieve top-10 relevant chunks (more = better recall for vague questions) ---
    try:
        top_chunks = search(query_embedding, store, top_k=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {e}")

    # --- Query the LLM ---
    try:
        answer = get_answer(question, top_chunks)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return ChatResponse(answer=answer)

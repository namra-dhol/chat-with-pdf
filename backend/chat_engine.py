"""
chat_engine.py
--------------
Supports two LLM backends via the LLM_PROVIDER env variable:
  - "groq"   → Groq cloud API via langchain-groq (free, fast)
  - "ollama" → local Ollama (needs `ollama serve`)

Config in backend/.env:
    LLM_PROVIDER=groq
    GROQ_API_KEY=gsk_...
    GROQ_MODEL=llama-3.3-70b-versatile
"""

import os
import json
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OLLAMA_URL   = os.getenv("OLLAMA_URL",  "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")


# ── Prompt builder ────────────────────────────────────────────────────────────
def build_prompt(question: str, context_chunks: List[str]) -> str:
    """Build a helpful RAG prompt that handles vague questions well."""
    context = "\n\n---\n\n".join(context_chunks)
    return f"""You are a helpful assistant answering questions about a document.

You have been given the most relevant sections of the document as context below.

Instructions:
- Answer the question using ONLY the provided context.
- If the context contains relevant information, explain it clearly even if the question is vague or short.
- If the context has partial information, share what you found and note what is missing.
- ONLY say "I don't have information about this in the document." if the context has NO relation to the question at all.
- Never invent facts outside the context.

Context from document:
{context}

Question: {question}

Answer:"""


# ── Groq backend (via langchain-groq — same as working demo) ─────────────────
def _ask_groq(prompt: str) -> str:
    """Query Groq using langchain-groq ChatGroq (matches the working Colab demo)."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to backend/.env"
        )

    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=1,
        )

        response = llm.invoke(prompt)
        return response.content.strip()

    except Exception as e:
        err_str = str(e)
        print(f"[ChatEngine] ❌ Groq error: {err_str}")
        if "401" in err_str or "invalid_api_key" in err_str:
            raise RuntimeError(
                "❌ Invalid Groq API Key. Check GROQ_API_KEY in backend/.env"
            )
        elif "429" in err_str or "rate_limit" in err_str:
            raise RuntimeError("⚠️ Groq rate limit reached. Wait a moment and try again.")
        elif "503" in err_str or "overloaded" in err_str.lower():
            raise RuntimeError("⚠️ Groq servers overloaded. Try again in a few seconds.")
        else:
            raise RuntimeError(f"Groq API error: {e}")


# ── Ollama backend ────────────────────────────────────────────────────────────
def _ask_ollama(prompt: str) -> str:
    """Query the local Ollama server."""
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure it is running: `ollama serve`"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama request timed out. Try again.")
    except (requests.exceptions.HTTPError, json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(f"Ollama error: {e}")


# ── Public entry point ────────────────────────────────────────────────────────
def get_answer(question: str, context_chunks: List[str]) -> str:
    """Route the question to the configured LLM and return the answer."""
    if not context_chunks:
        return "No relevant content was found in the document for your question."

    prompt = build_prompt(question, context_chunks)
    print(f"[ChatEngine] Using provider: {LLM_PROVIDER.upper()}")

    if LLM_PROVIDER == "groq":
        return _ask_groq(prompt)
    elif LLM_PROVIDER == "ollama":
        return _ask_ollama(prompt)
    else:
        raise RuntimeError(
            f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. "
            "Set LLM_PROVIDER=groq or LLM_PROVIDER=ollama in backend/.env"
        )

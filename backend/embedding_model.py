"""
embedding_model.py
------------------
Singleton wrapper around the sentence-transformers model.
Loads the model once and reuses it for all embedding requests.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

# --- Model Selection ---
# Using all-MiniLM-L6-v2 because it is:
#   - Lightweight (~80 MB) — fast to load and run on CPU
#   - Optimized for semantic similarity tasks
#   - Produces 384-dimensional embeddings — low memory footprint
#   - State-of-the-art performance on semantic search benchmarks
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Singleton: loaded once when the module is first imported
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Load and cache the embedding model (lazy initialization)."""
    global _model
    if _model is None:
        print(f"[Embedding] Loading model: {MODEL_NAME} ...")
        _model = SentenceTransformer(MODEL_NAME)
        print(f"[Embedding] Model loaded successfully.")
    return _model


def get_embedding(text: str) -> np.ndarray:
    """
    Generate a single embedding vector for a given text.

    Args:
        text: Input string to embed.

    Returns:
        A 1-D numpy array of shape (384,).
    """
    model = _get_model()
    return model.encode(text, convert_to_numpy=True)


def get_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    Generate embeddings for a list of text chunks (batched for efficiency).

    Args:
        texts: List of input strings.

    Returns:
        A list of 1-D numpy arrays, one per input text.
    """
    model = _get_model()
    # encode() with a list returns a 2D numpy array; we convert to a list of 1D arrays
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return [embeddings[i] for i in range(len(embeddings))]

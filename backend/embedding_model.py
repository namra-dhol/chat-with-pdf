"""
embedding_model.py
------------------
Wrapper that uses the HuggingFace Inference API to get embeddings remotely
via the official huggingface_hub client.
"""

import os
import numpy as np
from typing import List
from huggingface_hub import InferenceClient

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Initialize the client. It automatically picks up HF_TOKEN from environment.
_client = None

def _get_client():
    global _client
    if _client is None:
        token = os.getenv("HF_TOKEN")
        _client = InferenceClient(model=MODEL_NAME, token=token)
        if not token:
            print("[Embedding] Warning: No HF_TOKEN set. Expected rate limits.")
    return _client

def get_embedding(text: str) -> np.ndarray:
    """
    Generate a single embedding vector for a given text.
    """
    client = _get_client()
    try:
        res = client.feature_extraction(text)
        return np.array(res)
    except Exception as e:
        raise RuntimeError(f"HuggingFace API error: {e}")

def get_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    Generate embeddings for a list of text chunks in batches.
    """
    if not texts:
        return []

    client = _get_client()
    all_embeddings = []
    
    # Process in batches of 20 to avoid payload limits and timeouts
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            res = client.feature_extraction(batch)
            # res is a list of lists of floats or numpy array depending on version
            if isinstance(res, np.ndarray):
                all_embeddings.extend(res)
            else:
                for emb in res:
                    all_embeddings.append(np.array(emb))
        except Exception as e:
            raise RuntimeError(f"HuggingFace API batch error: {e}")

    return all_embeddings

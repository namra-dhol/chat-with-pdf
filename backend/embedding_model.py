"""
embedding_model.py
------------------
Wrapper that uses the HuggingFace Inference API to get embeddings remotely.
This avoids loading PyTorch and the model locally, saving >500MB of RAM.
"""

import os
import requests
import numpy as np
from typing import List

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL_NAME}"

def _get_headers():
    token = os.getenv("HF_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def get_embedding(text: str) -> np.ndarray:
    """
    Generate a single embedding vector for a given text using HF Inference API.
    """
    headers = _get_headers()
    response = requests.post(API_URL, headers=headers, json={"inputs": [text], "options": {"wait_for_model": True}})
    
    if not response.ok:
        raise RuntimeError(f"HuggingFace API error: {response.text}")
        
    data = response.json()
    # The API returns a list of lists when given a list of inputs
    return np.array(data[0])

def get_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    Generate embeddings for a list of text chunks using HF Inference API.
    """
    if not texts:
        return []
        
    headers = _get_headers()
    response = requests.post(API_URL, headers=headers, json={"inputs": texts, "options": {"wait_for_model": True}})
    
    if not response.ok:
        raise RuntimeError(f"HuggingFace API error: {response.text}")
        
    data = response.json()
    return [np.array(emb) for emb in data]

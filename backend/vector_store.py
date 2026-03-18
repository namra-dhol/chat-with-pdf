"""
vector_store.py
---------------
Handles saving and loading the pickle store, and similarity search.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple


# Default path for the pickle data file
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DEFAULT_PKL_PATH = os.path.join(DATA_DIR, "my_data.pkl")


def save_store(chunks: List[str], embeddings: List[np.ndarray], path: str = DEFAULT_PKL_PATH) -> None:
    """
    Serialize chunks and their embeddings to a pickle file.

    Args:
        chunks:     List of text chunk strings.
        embeddings: Corresponding list of embedding vectors.
        path:       File path where the .pkl file will be saved.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data_to_save = {
        "chunks": chunks,
        "embeddings": embeddings,   # List of np.ndarray
    }

    with open(path, "wb") as file:
        pickle.dump(data_to_save, file)

    print(f"[VectorStore] Saved {len(chunks)} chunks to '{path}'.")


def load_store(path: str = DEFAULT_PKL_PATH) -> Dict[str, Any]:
    """
    Load the pickle store from disk.

    Args:
        path: Path to the .pkl file.

    Returns:
        A dict with keys: 'chunks' (List[str]) and 'embeddings' (List[np.ndarray]).

    Raises:
        FileNotFoundError: If no .pkl file exists yet (PDF not uploaded).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            "No processed PDF found. Please upload a PDF first via POST /upload-pdf."
        )

    with open(path, "rb") as file:
        data = pickle.load(file)

    print(f"[VectorStore] Loaded {len(data['chunks'])} chunks from '{path}'.")
    return data


def search(
    query_embedding: np.ndarray,
    store: Dict[str, Any],
    top_k: int = 5,
) -> List[str]:
    """
    Find the top-k most similar chunks to the query embedding using cosine similarity.

    Args:
        query_embedding: 1-D numpy array for the user question.
        store:           The loaded pickle store dict.
        top_k:           Number of top results to return.

    Returns:
        A list of the top-k chunk strings, ranked by similarity (most similar first).
    """
    chunks: List[str] = store["chunks"]
    embeddings: List[np.ndarray] = store["embeddings"]

    if not chunks:
        return []

    # Stack embeddings into a 2D matrix: shape (num_chunks, embedding_dim)
    embedding_matrix = np.vstack(embeddings)

    # Compute cosine similarity using pure numpy (dot product over norms)
    query_norm = np.linalg.norm(query_embedding)
    if query_norm == 0:
        similarities = np.zeros(embedding_matrix.shape[0])
    else:
        dots = np.dot(embedding_matrix, query_embedding)
        norms = np.linalg.norm(embedding_matrix, axis=1)
        # Avoid division by zero
        norms[norms == 0] = 1 
        similarities = dots / (norms * query_norm)

    # Get indices of top-k most similar chunks
    top_indices = np.argsort(similarities)[::-1][:top_k]

    top_chunks = [chunks[i] for i in top_indices]
    top_scores = [float(similarities[i]) for i in top_indices]

    print(f"[VectorStore] Top-{top_k} similarities: {[f'{s:.3f}' for s in top_scores]}")

    return top_chunks

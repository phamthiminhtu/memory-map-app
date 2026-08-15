import pickle
import os
from typing import Any

def save_index(index: Any, path: str):
    """Save FAISS index and metadata to disk"""
    with open(path, 'wb') as f:
        pickle.dump(index, f)

def load_index(path: str) -> Any:
    """Load FAISS index and metadata from disk"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"No index found at {path}")
    with open(path, 'rb') as f:
        return pickle.load(f) 
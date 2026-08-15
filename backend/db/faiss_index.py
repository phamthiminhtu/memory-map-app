import faiss
import numpy as np
from typing import List, Dict, Any

class FAISSIndex:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []
    
    def add(self, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Add a new embedding with metadata"""
        self.index.add(embedding.reshape(1, -1))
        self.metadata.append(metadata)
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)
        return [self.metadata[i] for i in indices[0]] 
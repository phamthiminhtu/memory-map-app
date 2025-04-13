from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import os
import hashlib

class BaseDataLoader(ABC):
    def __init__(self, vector_db):
        self.vector_db = vector_db
    
    @abstractmethod
    def process_data(self, data_path: str) -> np.ndarray:
        """Process the data and return embeddings"""
        pass
    
    def _generate_doc_id(self, text: Optional[str] = None, file_path: Optional[str] = None) -> str:
        """Generate a unique document ID based on content or file path"""
        if text:
            content = text.encode('utf-8')
        elif file_path:
            content = file_path.encode('utf-8')
        else:
            raise ValueError("Either text or file_path must be provided")
        
        return hashlib.sha256(content).hexdigest()
    
    def save_memory(self, embedding: np.ndarray, metadata: Dict[str, Any]):
        """
        Save a memory with its embedding and metadata in a structured format
        
        Args:
            embedding (np.ndarray): The embedding vector
            metadata (Dict[str, Any]): Metadata including type, source, and file info
        """
        # Generate doc_id based on content type
        if metadata['type'] == 'text':
            with open(metadata['source'], 'r', encoding='utf-8') as f:
                text_content = f.read()
            doc_id = self._generate_doc_id(text=text_content)
            text = text_content
            image = None
        else:  # type == 'image'
            doc_id = self._generate_doc_id(file_path=metadata.get('source'))
            text = None
            image = metadata.get('source')
        
        # Create structured record
        record = {
            'doc_id': doc_id,
            'text': text,
            'image': image,
            'embedding': embedding,
            'metadata': metadata  # Store full metadata for reference
        }
        
        # Save to vector DB
        self.vector_db.add_memory(record)
    
    def load_memories(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Load k most similar memories"""
        return self.vector_db.search(query_embedding, k) 
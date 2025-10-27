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
    
    @abstractmethod
    def generate_query_embedding(self, query: str):
        """
        Generate an embedding for a query using the embedding function
        
        Args:
            query (str): The query to generate an embedding for
        """
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
            text = metadata['text']
            doc_id = self._generate_doc_id(text=text)
            image = None
        else:  # type == 'image'
            doc_id = self._generate_doc_id(file_path=metadata.get('source'))
            text = None
            image = metadata.get('source')
        
        # Create structured record
        record = {
            'metadata': metadata,  # Store full metadata for reference
            'doc_id': doc_id,
            'document': text if text else image,
            'embedding': embedding 
        }

        # Save to vector DB
        self.vector_db.add_memory(record=record)
    
    def load_memories(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Load k most similar memories"""
        return self.vector_db.search(query_embedding, k) 

    def delete_memory(self, doc_id: str):
        """Delete a memory by its document ID"""
        self.vector_db.delete_memory(doc_id)

        return f"Memory with doc_id {doc_id} deleted"
    
    def delete_all_memories(self):
        """Delete all memories"""
        deleted_memories = []
        for memory in self.vector_db.get_all_memories():
            self.vector_db.delete_memory(memory['doc_id'])
            deleted_memories.append(memory['doc_id'])

        return f"Total {len(deleted_memories)} memories deleted: {deleted_memories}"

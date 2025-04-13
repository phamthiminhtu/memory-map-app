from .base_loader import BaseDataLoader
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, Any
from utils.text_cleaning import clean_text, split_into_chunks

class TextDataLoader(BaseDataLoader):
    def __init__(self, vector_db, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(vector_db)
        self.model = SentenceTransformer(model_name)
    
    def process_data(self, text_path: str) -> np.ndarray:
        """
        Process text data and return embeddings
        
        Args:
            text_path (str): Path to the text file
            
        Returns:
            np.ndarray: Text embeddings
        """
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Clean and preprocess text
        cleaned_text = clean_text(text)
        
        # Split into chunks if text is too long
        chunks = split_into_chunks(cleaned_text)
        
        # Generate embeddings for each chunk
        embeddings = self.model.encode(chunks)
        
        # If multiple chunks, average the embeddings
        if len(embeddings.shape) > 1:
            embeddings = np.mean(embeddings, axis=0)
        
        return embeddings
    
    def save_text_memory(self, text_path: str, metadata: Dict[str, Any] = None):
        """
        Process text, generate embeddings, and save to vector DB
        
        Args:
            text_path (str): Path to the text file
            metadata (Dict[str, Any]): Additional metadata to store
        """
        if metadata is None:
            metadata = {}
        
        # Add text-specific metadata
        metadata['type'] = 'text'
        metadata['source'] = text_path
        
        # Process text and get embeddings
        embeddings = self.process_data(text_path)
        
        # Save to vector DB with structured format
        self.save_memory(embeddings, metadata) 
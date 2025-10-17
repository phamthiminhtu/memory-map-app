from etl.data_loaders.base_loader import BaseDataLoader
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, Any
from utils.text_cleaning import clean_text, split_into_chunks

class TextDataLoader(BaseDataLoader):
    def __init__(self, vector_db, persist_directory: str = 'data/embeded_text', model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(vector_db)
        self.persist_directory = persist_directory
        self.model = SentenceTransformer(model_name)

    def load_text(self, text_path: str = None, text: str = None) -> str:
        if text_path is not None:
            with open(text_path, 'r') as file:
                text = file.read()
        elif text is None:
            raise ValueError("Either text_path or text must be provided")
        return text

    def process_data(self, text: str) -> np.ndarray:
        """
        Process text data and return embeddings
        
        Args:
            text_path (str, optional): Path to the text file
            text (str, optional): Direct text content to process
            
        Returns:
            np.ndarray: Text embeddings
        """
            
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

    def generate_query_embedding(self, query: str):
        """
        Generate an embedding for a query using the embedding function
        
        Args:
            query (str): The query to generate an embedding for
        """
        embeddings = self.process_data(text=query)

        return embeddings
    
    def save_text_memory(self, text_path: str = None, text: str = None, metadata: Dict[str, Any] = None):
        """
        Process text, generate embeddings, and save to vector DB

        Args:
            text_path (str): Path to the text file
            metadata (Dict[str, Any]): Additional metadata to store
        """
        from datetime import datetime

        text = self.load_text(text_path=text_path, text=text)

        if metadata is None:
            metadata = {}

        # Add timestamp if not present
        if 'timestamp' not in metadata and 'date' not in metadata:
            metadata['timestamp'] = datetime.now().isoformat()

        # Add text-specific metadata
        metadata['type'] = 'text'
        metadata['source'] = text_path
        metadata['text'] = text

        # Process text and get embeddings
        embeddings = self.process_data(text=text)

        # Save to vector DB with structured format
        self.save_memory(embedding=embeddings, metadata=metadata) 
from etl.data_loaders.text_loader import TextDataLoader
from etl.data_loaders.image_loader import ImageDataLoader
from typing import Dict, Any, List, Tuple
import numpy as np
from db.chroma_db import ChromaDB

class MemoryRetriever:
    def __init__(
        self, 
        text_persist_directory: str = 'data/embeded_text', 
        image_persist_directory: str = 'data/embeded_image', 
        text_model_name: str = "all-MiniLM-L6-v2", 
        image_model_name: str = "ViT-B/32"
    ):
        """
        Initialize UnifiedMemoryRetriever for searching both text and image memories
        
        Args:
            vector_db: Vector database instance
            text_model_name (str): Name of the text embedding model
            image_model_name (str): Name of the image embedding model
        """
        
        self.text_chroma_db = ChromaDB(persist_directory=text_persist_directory)
        self.image_chroma_db = ChromaDB(persist_directory=image_persist_directory)
        self.text_loader = TextDataLoader(self.text_chroma_db, model_name=text_model_name)
        self.image_loader = ImageDataLoader(self.image_chroma_db, model_name=image_model_name)
    
    def search_memories(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for both text and image memories relevant to the query
        
        Args:
            query (str): The search query
            k (int): Number of results to return per type
            
        Returns:
            List[Dict[str, Any]]: Combined list of relevant text and image memories
        """
        
        # Search for text memories
        text_memories = self.text_chroma_db.search_memories(
            query=query, 
            query_embedding_function=self.text_loader.generate_query_embedding,
            n_results=n_results
        )
        
        # Search for image memories
        image_memories = self.image_chroma_db.search_memories(
            query=query, 
            query_embedding_function=self.image_loader.generate_query_embedding,
            n_results=n_results
        )
        
        # Combine and sort results by relevance
        all_memories = text_memories + image_memories
        
        # Sort by distance if available
        all_memories.sort(key=lambda x: x.get('distance', float('inf')))
        
        return all_memories 
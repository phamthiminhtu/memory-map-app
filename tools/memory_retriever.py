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
        image_model_name: str = "ViT-B/32",
        similarity_threshold: float = 0.7  # Higher threshold means more strict matching
    ):
        """
        Initialize UnifiedMemoryRetriever for searching both text and image memories
        
        Args:
            text_persist_directory (str): Directory to store text embeddings
            image_persist_directory (str): Directory to store image embeddings
            text_model_name (str): Name of the text embedding model
            image_model_name (str): Name of the image embedding model
            similarity_threshold (float): Threshold for considering a result relevant (0-1)
        """
        self.text_chroma_db = ChromaDB(persist_directory=text_persist_directory)
        self.image_chroma_db = ChromaDB(persist_directory=image_persist_directory)
        self.text_loader = TextDataLoader(self.text_chroma_db, model_name=text_model_name)
        self.image_loader = ImageDataLoader(self.image_chroma_db, model_name=image_model_name)

    
    def search_memories(self, query: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """
        Search for both text and image memories relevant to the query
        
        Args:
            query (str): The search query
            n_results (int): Number of results to return per type
            
        Returns:
            List[Dict[str, Any]]: Combined list of relevant text and image memories
        """
        # Search for text memories
        text_memories = self.text_chroma_db.search_memories(
            query=query, 
            query_embedding_function=self.text_loader.generate_query_embedding,
            n_results=max(n_results*2, 5)
        )
        
        # Search for image memories
        image_memories = self.image_chroma_db.search_memories(
            query=query, 
            query_embedding_function=self.image_loader.generate_query_embedding,
            n_results=max(n_results*2, 5)
        )
        
        # Filter and combine results
        relevant_memories = text_memories + image_memories
        print(relevant_memories)
        # Sort by distance
        relevant_memories.sort(key=lambda x: x.get('distance', float('inf')))

        return relevant_memories[0:n_results]
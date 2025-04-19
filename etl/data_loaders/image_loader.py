from etl.data_loaders.base_loader import BaseDataLoader
from PIL import Image
import torch
# from transformers import AutoImageProcessor, AutoModel
import numpy as np
import clip
from typing import Dict, Any

class ImageDataLoader(BaseDataLoader):
    def __init__(self, vector_db, model_name: str = "ViT-B/32"):
        super().__init__(vector_db)
        self.model, self.processor = clip.load(model_name)
    
    def process_data(self, image_path: str) -> np.ndarray:
        """
        Process image data and return embeddings
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            np.ndarray: Image embeddings
        """
        # Load and preprocess image
        image = Image.open(image_path).convert("RGB")
        image_input = self.processor(image).unsqueeze(0)
        
        # Generate embeddings
        with torch.no_grad():
            image_embedding = self.model.encode_image(image_input).squeeze().numpy().tolist()
        
        return image_embedding
    
    def generate_query_embedding(self, query: str):
        """
        Generate an embedding for a query using the embedding function
        
        Args:
            query (str): The query to generate an embedding 
            model (Any): The model to use for embedding generation
        """
        tokenized_query = clip.tokenize(query)
        query_embedding_tensor = self.model.encode_text(tokenized_query)
        query_embedding = query_embedding_tensor.detach().numpy().tolist()
        
        return query_embedding
    
    def save_image_memory(self, image_path: str, metadata: Dict[str, Any] = None):
        """
        Process image, generate embeddings, and save to vector DB
        
        Args:
            image_path (str): Path to the image file
            metadata (Dict[str, Any]): Additional metadata to store
        """
        if metadata is None:
            metadata = {}
        
        # Add image-specific metadata
        metadata['type'] = 'image'
        metadata['source'] = image_path
        
        # Process image and get embeddings
        embedding = self.process_data(image_path)
        
        # Save to vector DB with structured format
        self.save_memory(embedding=embedding, metadata=metadata) 
from .base_loader import BaseDataLoader
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModel
import numpy as np
from typing import Dict, Any

class ImageDataLoader(BaseDataLoader):
    def __init__(self, vector_db, model_name: str = "microsoft/resnet-50"):
        super().__init__(vector_db)
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
    
    def process_data(self, image_path: str) -> np.ndarray:
        """
        Process image data and return embeddings
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            np.ndarray: Image embeddings
        """
        # Load and preprocess image
        image = Image.open(image_path)
        inputs = self.processor(image, return_tensors="pt")
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get the pooled output (usually the [CLS] token embedding)
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
        
        return embeddings
    
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
        embeddings = self.process_data(image_path)
        
        # Save to vector DB with structured format
        self.save_memory(embeddings, metadata) 
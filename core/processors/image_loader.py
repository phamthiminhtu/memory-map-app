from core.processors.base_loader import BaseDataLoader
from PIL import Image
import torch
import numpy as np
import clip
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.disable(logging.CRITICAL)

class ImageDataLoader(BaseDataLoader):
    def __init__(self, vector_db, model_name: str = "ViT-B/32"):
        """
        Initialize CLIP model for both image and text processing
        """
        super().__init__(vector_db)
        logger.info(f"Loading CLIP model: {model_name}")
        self.model, self.processor = clip.load(model_name)
        
        # Store embedding dimension
        self.embedding_dim = 512  # CLIP ViT-B/32 dimension
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def _get_metadata_text(self, metadata: Dict[str, Any]) -> str:
        """
        Convert metadata to searchable text
        """
        text_parts = []
        
        # Add tags if present
        if 'tags' in metadata:
            text_parts.append(str(metadata['tags']))
            
        # Add title if present
        if 'title' in metadata:
            text_parts.append(str(metadata['title']))
            
        # Add description if present
        if 'description' in metadata:
            text_parts.append(str(metadata['description']))
        
        result = " ".join(text_parts)
        logger.debug(f"Generated metadata text: {result}")
        return result
    
    def _get_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate text embedding using CLIP
        """
        text_input = clip.tokenize([text])
        with torch.no_grad():
            text_embedding = self.model.encode_text(text_input).squeeze().numpy()
        return text_embedding / np.linalg.norm(text_embedding)
    
    def _combine_embeddings(self, image_embedding: np.ndarray, metadata_embedding: np.ndarray, alpha: float = 0.7) -> np.ndarray:
        """
        Combine image and metadata embeddings
        """
        try:
            # Check dimensions
            if image_embedding.shape[0] != self.embedding_dim:
                raise ValueError(f"Image embedding dimension mismatch. Expected {self.embedding_dim}, got {image_embedding.shape[0]}")
            if metadata_embedding.shape[0] != self.embedding_dim:
                raise ValueError(f"Text embedding dimension mismatch. Expected {self.embedding_dim}, got {metadata_embedding.shape[0]}")
            
            # Combine with weighted average
            combined = (alpha * image_embedding) + ((1 - alpha) * metadata_embedding)
            
            # Normalize the result
            combined = combined / np.linalg.norm(combined)
            
            logger.debug(f"Combined embedding shape: {combined.shape}")
            return combined
            
        except Exception as e:
            logger.error(f"Error combining embeddings: {str(e)}")
            raise
    
    def process_data(self, image_path: str, metadata: Dict[str, Any] = None) -> np.ndarray:
        """
        Process image and metadata to generate combined embedding
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Load and process image
            image = Image.open(image_path).convert("RGB")
            image_input = self.processor(image).unsqueeze(0)
            
            # Generate image embedding
            with torch.no_grad():
                image_embedding = self.model.encode_image(image_input).squeeze().numpy()
                image_embedding = image_embedding / np.linalg.norm(image_embedding)
            
            logger.debug(f"Image embedding shape: {image_embedding.shape}")
            
            # If no metadata, return just the image embedding
            if not metadata:
                logger.info("No metadata provided, using image embedding only")
                return image_embedding
            
            # Get metadata text and generate embedding
            metadata_text = self._get_metadata_text(metadata)
            if metadata_text:
                logger.info("Generating metadata embedding")
                metadata_embedding = self._get_text_embedding(metadata_text)
                logger.debug(f"Metadata embedding shape: {metadata_embedding.shape}")
                # Combine embeddings
                return self._combine_embeddings(image_embedding, metadata_embedding)
            
            logger.info("No metadata text generated, using image embedding only")
            return image_embedding
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a text query using CLIP
        """
        try:
            logger.info(f"Generating query embedding for: {query}")
            query_embedding = self._get_text_embedding(query)
            logger.debug(f"Query embedding shape: {query_embedding.shape}")
            return query_embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def save_image_memory(self, image_path: str, metadata: Dict[str, Any] = None):
        """
        Process image and metadata, generate embeddings, and save to vector DB
        """
        try:
            from datetime import datetime
            import os

            logger.info(f"Saving image memory: {image_path}")

            if metadata is None:
                metadata = {}

            # Add timestamp if not present - try file modification time first
            if 'timestamp' not in metadata and 'date' not in metadata:
                try:
                    # Use file modification time if available
                    if os.path.exists(image_path):
                        mtime = os.path.getmtime(image_path)
                        metadata['timestamp'] = datetime.fromtimestamp(mtime).isoformat()
                    else:
                        metadata['timestamp'] = datetime.now().isoformat()
                except:
                    metadata['timestamp'] = datetime.now().isoformat()

            # Add image-specific metadata
            metadata['type'] = 'image'
            metadata['source'] = image_path

            # Process image and metadata to get combined embedding
            embedding = self.process_data(image_path, metadata)

            # Save to vector DB with structured format
            self.save_memory(embedding, metadata)
            logger.info("Successfully saved image memory")

        except Exception as e:
            logger.error(f"Error saving image memory: {str(e)}")
            raise 
"""Dependency injection for FastAPI routes."""

from functools import lru_cache
from backend.services.memory_service import MemoryService
import os


@lru_cache()
def get_memory_service() -> MemoryService:
    """
    Get or create a singleton MemoryService instance.

    This uses lru_cache to ensure we only create one instance
    of the MemoryService throughout the application lifecycle.

    Returns:
        MemoryService: Configured memory service instance
    """
    # Get configuration from environment or use defaults
    text_persist_dir = os.getenv('TEXT_PERSIST_DIR', 'data/chroma_text')
    image_persist_dir = os.getenv('IMAGE_PERSIST_DIR', 'data/chroma_image')
    text_model_name = os.getenv('TEXT_MODEL_NAME', 'all-MiniLM-L6-v2')
    image_model_name = os.getenv('IMAGE_MODEL_NAME', 'ViT-B/32')

    return MemoryService(
        text_persist_dir=text_persist_dir,
        image_persist_dir=image_persist_dir,
        text_model_name=text_model_name,
        image_model_name=image_model_name
    )

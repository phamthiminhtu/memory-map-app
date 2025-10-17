"""
Memory Service - Business Logic Layer

This service encapsulates all memory management operations and provides
a clean interface for both the Streamlit app and MCP server.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from db.chroma_db import ChromaDB
from etl.data_loaders.text_loader import TextDataLoader
from etl.data_loaders.image_loader import ImageDataLoader
from tools.memory_retriever import MemoryRetriever


@dataclass
class MemoryStats:
    """Statistics about stored memories."""
    total_count: int
    text_count: int
    image_count: int


@dataclass
class SearchResult:
    """Result from a memory search."""
    memories: List[Dict[str, Any]]
    query: str
    count: int


class MemoryService:
    """Service for managing and searching memories."""

    def __init__(
        self,
        text_persist_dir: str = 'data/chroma_text',
        image_persist_dir: str = 'data/chroma_image',
        text_model_name: str = "all-MiniLM-L6-v2",
        image_model_name: str = "ViT-B/32"
    ):
        """
        Initialize the memory service with database connections and loaders.

        Args:
            text_persist_dir: Directory for text database
            image_persist_dir: Directory for image database
            text_model_name: Model name for text embeddings
            image_model_name: Model name for image embeddings
        """
        # Initialize databases
        self.text_db = ChromaDB(persist_directory=text_persist_dir)
        self.image_db = ChromaDB(persist_directory=image_persist_dir)

        # Initialize data loaders
        self.text_loader = TextDataLoader(
            vector_db=self.text_db,
            model_name=text_model_name
        )
        self.image_loader = ImageDataLoader(
            vector_db=self.image_db,
            model_name=image_model_name
        )

        # Initialize retriever
        self.retriever = MemoryRetriever(
            text_persist_directory=text_persist_dir,
            image_persist_directory=image_persist_dir,
            text_model_name=text_model_name,
            image_model_name=image_model_name
        )

    def search_memories(
        self,
        query: str,
        n_results: int = 5
    ) -> SearchResult:
        """
        Search for memories using natural language query.

        Args:
            query: Natural language search query
            n_results: Number of results to return

        Returns:
            SearchResult object containing matching memories
        """
        # Validate n_results
        n_results = max(1, min(20, n_results))

        # Search using the retriever
        results = self.retriever.search_memories(query, n_results=n_results)

        return SearchResult(
            memories=results,
            query=query,
            count=len(results)
        )

    def add_text_memory(
        self,
        text: str,
        title: Optional[str] = None,
        tags: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Add a new text memory.

        Args:
            text: The text content
            title: Optional title
            tags: Optional comma-separated tags
            description: Optional description

        Returns:
            Document ID of the created memory
        """
        # Prepare metadata
        metadata = {}
        if title:
            metadata['title'] = title
        if tags:
            metadata['tags'] = tags
        if description:
            metadata['description'] = description

        # Save the memory
        self.text_loader.save_text_memory(
            text=text,
            metadata=metadata if metadata else None
        )

        # Generate and return doc_id
        doc_id = self.text_loader._generate_doc_id(text=text)
        return doc_id

    def add_image_memory(
        self,
        image_path: str,
        title: Optional[str] = None,
        tags: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Add a new image memory.

        Args:
            image_path: Path to the image file
            title: Optional title
            tags: Optional comma-separated tags
            description: Optional description

        Returns:
            Document ID of the created memory
        """
        # Prepare metadata
        metadata = {}
        if title:
            metadata['title'] = title
        if tags:
            metadata['tags'] = tags
        if description:
            metadata['description'] = description

        # Save the memory
        self.image_loader.save_image_memory(
            image_path=image_path,
            metadata=metadata if metadata else None
        )

        # Generate and return doc_id
        doc_id = self.image_loader._generate_doc_id(file_path=image_path)
        return doc_id

    def get_memory_stats(self) -> MemoryStats:
        """
        Get statistics about stored memories.

        Returns:
            MemoryStats object with counts
        """
        text_memories = self.text_db.get_all_memories()
        image_memories = self.image_db.get_all_memories()

        text_count = len(text_memories)
        image_count = len(image_memories)
        total_count = text_count + image_count

        return MemoryStats(
            total_count=total_count,
            text_count=text_count,
            image_count=image_count
        )

    def list_recent_memories(
        self,
        limit: int = 10,
        memory_type: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        List recent memories.

        Args:
            limit: Maximum number of memories to return
            memory_type: Type filter - "text", "image", or "all"

        Returns:
            List of memory dictionaries
        """
        # Validate limit
        limit = max(1, min(50, limit))

        memories = []

        # Get text memories if requested
        if memory_type in ["text", "all"]:
            text_memories = self.text_db.get_all_memories()
            for mem in text_memories[:limit]:
                if 'metadata' not in mem:
                    mem['metadata'] = {}
                mem['metadata']['type'] = 'text'
                memories.append(mem)

        # Get image memories if requested
        if memory_type in ["image", "all"]:
            image_memories = self.image_db.get_all_memories()
            for mem in image_memories[:limit]:
                if 'metadata' not in mem:
                    mem['metadata'] = {}
                mem['metadata']['type'] = 'image'
                memories.append(mem)

        # Limit total results
        return memories[:limit]

    def delete_memory(self, doc_id: str, memory_type: str = "text") -> bool:
        """
        Delete a memory by ID.

        Args:
            doc_id: Document ID to delete
            memory_type: Type of memory - "text" or "image"

        Returns:
            True if successful, False otherwise
        """
        try:
            if memory_type == "text":
                return self.text_db.delete_memory(doc_id)
            elif memory_type == "image":
                return self.image_db.delete_memory(doc_id)
            else:
                return False
        except Exception:
            return False

    def get_text_memories(self) -> List[Dict[str, Any]]:
        """Get all text memories."""
        return self.text_db.get_all_memories()

    def get_image_memories(self) -> List[Dict[str, Any]]:
        """Get all image memories."""
        return self.image_db.get_all_memories()

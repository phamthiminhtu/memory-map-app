"""
Memory Service - Business Logic Layer

This service encapsulates all memory management operations and provides
a clean interface for both the Streamlit app and MCP server.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from dateutil import parser as date_parser
import re
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


@dataclass
class SynthesisResult:
    """Result from synthesizing multiple memory sources."""
    text_memories: List[Dict[str, Any]]
    image_memories: List[Dict[str, Any]]
    combined_count: int
    timeline: List[Dict[str, Any]]  # Sorted by date
    synthesis_summary: str


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

    def search_text_memories_only(
        self,
        query: str,
        n_results: int = 5
    ) -> SearchResult:
        """
        Search ONLY text memories.

        Args:
            query: Natural language search query
            n_results: Number of results to return

        Returns:
            SearchResult object containing matching text memories
        """
        n_results = max(1, min(20, n_results))

        results = self.text_db.search_memories(
            query=query,
            query_embedding_function=self.text_loader.generate_query_embedding,
            n_results=n_results
        )

        # Ensure type metadata is set
        for result in results:
            if 'metadata' not in result:
                result['metadata'] = {}
            result['metadata']['type'] = 'text'

        return SearchResult(
            memories=results,
            query=query,
            count=len(results)
        )

    def search_image_memories_only(
        self,
        query: str,
        n_results: int = 5
    ) -> SearchResult:
        """
        Search ONLY image memories.

        Args:
            query: Natural language search query
            n_results: Number of results to return

        Returns:
            SearchResult object containing matching image memories
        """
        n_results = max(1, min(20, n_results))

        results = self.image_db.search_memories(
            query=query,
            query_embedding_function=self.image_loader.generate_query_embedding,
            n_results=n_results
        )

        # Ensure type metadata is set
        for result in results:
            if 'metadata' not in result:
                result['metadata'] = {}
            result['metadata']['type'] = 'image'

        return SearchResult(
            memories=results,
            query=query,
            count=len(results)
        )

    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """
        Extract date from text content using various patterns.

        Returns ISO format date string or None.
        """
        try:
            # Try common date patterns
            date_patterns = [
                r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
                r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # MM/DD/YYYY
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
                r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',  # DD Mon YYYY
            ]

            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        parsed_date = date_parser.parse(match.group(0))
                        return parsed_date.date().isoformat()
                    except:
                        continue

            return None
        except:
            return None

    def _filter_by_date_range(
        self,
        memories: List[Dict[str, Any]],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter memories by date range.

        Args:
            memories: List of memory dictionaries
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
        """
        if not start_date and not end_date:
            return memories

        filtered = []

        for memory in memories:
            metadata = memory.get('metadata', {})

            # Try to get date from metadata first
            memory_date_str = metadata.get('date') or metadata.get('timestamp')

            # If not in metadata, try to extract from text content
            if not memory_date_str:
                text_content = metadata.get('text', memory.get('text', ''))
                memory_date_str = self._extract_date_from_text(text_content)

            if memory_date_str:
                try:
                    memory_date = date_parser.parse(memory_date_str).date()

                    # Check if within range
                    if start_date:
                        start = date_parser.parse(start_date).date()
                        if memory_date < start:
                            continue

                    if end_date:
                        end = date_parser.parse(end_date).date()
                        if memory_date > end:
                            continue

                    filtered.append(memory)
                except:
                    # If date parsing fails, skip filtering for this memory
                    filtered.append(memory)
            else:
                # If no date found, include in results
                filtered.append(memory)

        return filtered

    def search_memories_by_date(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        n_results: int = 10
    ) -> SearchResult:
        """
        Search memories within a specific date range.

        Args:
            query: Natural language search query
            start_date: Start date in ISO format (YYYY-MM-DD) or natural language
            end_date: End date in ISO format (YYYY-MM-DD) or natural language
            n_results: Number of results to return

        Returns:
            SearchResult with filtered memories
        """
        # Parse natural language dates if needed
        if start_date and not re.match(r'\d{4}-\d{2}-\d{2}', start_date):
            try:
                start_date = date_parser.parse(start_date).date().isoformat()
            except:
                start_date = None

        if end_date and not re.match(r'\d{4}-\d{2}-\d{2}', end_date):
            try:
                end_date = date_parser.parse(end_date).date().isoformat()
            except:
                end_date = None

        # Get more results than needed for filtering
        search_multiplier = 3
        all_results = self.retriever.search_memories(
            query,
            n_results=n_results * search_multiplier
        )

        # Filter by date range
        filtered = self._filter_by_date_range(all_results, start_date, end_date)

        # Limit to requested number
        filtered = filtered[:n_results]

        return SearchResult(
            memories=filtered,
            query=query,
            count=len(filtered)
        )

    def synthesize_memories(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        n_results_per_type: int = 10
    ) -> SynthesisResult:
        """
        Synthesize memories from both text and image sources into a coherent timeline.

        This is the key method for agentic behavior - it searches both sources,
        filters by date, and creates a unified timeline.

        Args:
            query: Natural language search query
            start_date: Optional start date filter
            end_date: Optional end date filter
            n_results_per_type: Number of results to get per type

        Returns:
            SynthesisResult with combined and organized memories
        """
        # Search text memories
        text_results = self.search_text_memories_only(query, n_results_per_type)

        # Search image memories
        image_results = self.search_image_memories_only(query, n_results_per_type)

        # Filter by date if specified
        text_memories = text_results.memories
        image_memories = image_results.memories

        if start_date or end_date:
            text_memories = self._filter_by_date_range(text_memories, start_date, end_date)
            image_memories = self._filter_by_date_range(image_memories, start_date, end_date)

        # Create timeline - combine and sort by date
        all_memories = text_memories + image_memories
        timeline = self._create_timeline(all_memories)

        # Generate synthesis summary
        summary = self._generate_synthesis_summary(
            query=query,
            text_count=len(text_memories),
            image_count=len(image_memories),
            start_date=start_date,
            end_date=end_date
        )

        return SynthesisResult(
            text_memories=text_memories,
            image_memories=image_memories,
            combined_count=len(all_memories),
            timeline=timeline,
            synthesis_summary=summary
        )

    def _create_timeline(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create a chronological timeline from memories.

        Args:
            memories: List of memory dictionaries

        Returns:
            Sorted list of memories with date information
        """
        # Add parsed dates for sorting
        for memory in memories:
            metadata = memory.get('metadata', {})
            date_str = metadata.get('date') or metadata.get('timestamp')

            if not date_str:
                text_content = metadata.get('text', memory.get('text', ''))
                date_str = self._extract_date_from_text(text_content)

            if date_str:
                try:
                    memory['_parsed_date'] = date_parser.parse(date_str)
                except:
                    memory['_parsed_date'] = None
            else:
                memory['_parsed_date'] = None

        # Sort by date (None dates go to end)
        sorted_memories = sorted(
            memories,
            key=lambda x: x['_parsed_date'] if x['_parsed_date'] else datetime.max,
            reverse=False
        )

        # Remove temporary field
        for memory in sorted_memories:
            if '_parsed_date' in memory:
                del memory['_parsed_date']

        return sorted_memories

    def _generate_synthesis_summary(
        self,
        query: str,
        text_count: int,
        image_count: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """Generate a summary of the synthesis results."""
        parts = [f"Memory synthesis for query: '{query}'"]

        if start_date or end_date:
            date_range = []
            if start_date:
                date_range.append(f"from {start_date}")
            if end_date:
                date_range.append(f"to {end_date}")
            parts.append(f"Date range: {' '.join(date_range)}")

        parts.append(f"Found {text_count} text memories and {image_count} image memories")
        parts.append(f"Total: {text_count + image_count} memories")

        return "\n".join(parts)

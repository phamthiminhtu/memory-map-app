"""
Formatters for MCP server responses.

This module contains formatting logic for converting memory service results
into human-readable text responses for the MCP protocol.
"""

from typing import Dict, Any, List
from services.memory_service import SearchResult, SynthesisResult


class MCPFormatter:
    """Formatter for MCP server responses."""

    def __init__(self, max_text_length: int = 500):
        self.max_text_length = max_text_length

    def format_search_results(
        self,
        result: SearchResult,
        memory_type: str = "all"
    ) -> str:
        """Format standard search results."""
        if result.count == 0:
            return f"No {memory_type} memories found for query: '{result.query}'"

        parts = [f"Found {result.count} {memory_type} memories for '{result.query}':\n"]

        for idx, memory in enumerate(result.memories, 1):
            metadata = memory.get('metadata', {})
            mem_type = metadata.get('type', 'unknown')
            distance = memory.get('distance', 'N/A')

            parts.append(f"\n--- {mem_type.capitalize()} Memory {idx} ---")
            parts.append(f"Relevance Score: {distance:.4f}")
            parts.extend(self._format_metadata(metadata))
            parts.extend(self._format_content(metadata, memory, mem_type))

        return "\n".join(parts)

    def format_date_search(
        self,
        result: SearchResult,
        start_date: str,
        end_date: str = None
    ) -> str:
        """Format date-filtered search results."""
        date_info = f"from {start_date}" + (f" to {end_date}" if end_date else "")

        if result.count == 0:
            return f"No memories found for '{result.query}' {date_info}"

        parts = [f"Found {result.count} memories for '{result.query}' {date_info}:\n"]

        for idx, memory in enumerate(result.memories, 1):
            metadata = memory.get('metadata', {})
            memory_type = metadata.get('type', 'unknown')
            distance = memory.get('distance', 'N/A')

            parts.append(f"\n--- Memory {idx} ({memory_type}) ---")
            parts.append(f"Relevance Score: {distance:.4f}")
            parts.extend(self._format_metadata(metadata))
            parts.extend(self._format_content(metadata, memory, memory_type, max_len=400))

        return "\n".join(parts)

    def format_synthesis(self, result: SynthesisResult) -> str:
        """Format synthesis results with chronological timeline."""
        if result.combined_count == 0:
            return "No memories found for synthesis"

        parts = [
            "=== MEMORY SYNTHESIS ===\n",
            result.synthesis_summary,
            "\n" + "=" * 50 + "\n",
            "\nCHRONOLOGICAL TIMELINE:\n"
        ]

        for idx, memory in enumerate(result.timeline, 1):
            metadata = memory.get('metadata', {})
            memory_type = metadata.get('type', 'unknown')
            distance = memory.get('distance', 'N/A')
            date_val = metadata.get('date') or metadata.get('timestamp', 'Unknown date')

            parts.append(f"\n[{date_val}] Memory {idx} ({memory_type.upper()})")
            parts.append(f"  Relevance: {distance:.4f}")

            if metadata.get('title'):
                parts.append(f"  Title: {metadata['title']}")
            if metadata.get('tags'):
                parts.append(f"  Tags: {metadata['tags']}")

            if memory_type == 'text':
                text_content = metadata.get('text', memory.get('document', ''))
                if len(text_content) > 300:
                    text_content = text_content[:300] + "..."
                parts.append(f"  Content: {text_content}")
            elif memory_type == 'image':
                if metadata.get('description'):
                    parts.append(f"  Description: {metadata['description']}")
                parts.append(f"  Image: {metadata.get('source', 'N/A')}")

        parts.extend([
            "\n" + "=" * 50,
            f"\nSUMMARY: {len(result.text_memories)} text + {len(result.image_memories)} images = {result.combined_count} total memories",
            "\nUse this chronological timeline to craft a coherent narrative story for the user."
        ])

        return "\n".join(parts)

    def format_stats(self, text_count: int, image_count: int, total_count: int) -> str:
        """Format memory statistics."""
        return (
            f"Memory Statistics:\n\n"
            f"Total Memories: {total_count}\n"
            f"├── Text Memories: {text_count}\n"
            f"└── Image Memories: {image_count}"
        )

    def format_recent_memories(
        self,
        memories: List[Dict[str, Any]],
        memory_type: str = "all"
    ) -> str:
        """Format recent memories list."""
        if not memories:
            return f"No {memory_type} memories found."

        parts = [f"Recent {memory_type} memories (showing {len(memories)}):\n"]

        for idx, memory in enumerate(memories, 1):
            metadata = memory.get('metadata', {})
            mem_type = metadata.get('type', 'unknown')

            parts.append(f"\n--- Memory {idx} ({mem_type}) ---")
            parts.extend(self._format_metadata(metadata))
            parts.extend(self._format_content(metadata, memory, mem_type, max_len=300))

        return "\n".join(parts)

    def _format_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Format common metadata fields."""
        parts = []

        if metadata.get('title'):
            parts.append(f"Title: {metadata['title']}")

        if metadata.get('timestamp') or metadata.get('date'):
            date_val = metadata.get('date') or metadata.get('timestamp')
            parts.append(f"Date: {date_val}")

        if metadata.get('tags'):
            parts.append(f"Tags: {metadata['tags']}")

        return parts

    def _format_content(
        self,
        metadata: Dict[str, Any],
        memory: Dict[str, Any],
        mem_type: str,
        max_len: int = None
    ) -> List[str]:
        """Format memory content based on type."""
        parts = []
        max_length = max_len or self.max_text_length

        if mem_type == 'text':
            text_content = metadata.get('text', memory.get('document', ''))
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "..."
            parts.append(f"Content: {text_content}")
        elif mem_type == 'image':
            if metadata.get('description'):
                parts.append(f"Description: {metadata['description']}")
            parts.append(f"Image Path: {metadata.get('source', 'N/A')}")

        return parts

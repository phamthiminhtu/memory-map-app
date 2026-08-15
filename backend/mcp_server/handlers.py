"""
Tool handlers for MCP server.

This module contains the command pattern implementation for handling tool calls.
"""

from typing import Dict, Any, List
from mcp.types import TextContent
from backend.services.memory_service import MemoryService
from backend.mcp_server.formatters import MCPFormatter


class ToolHandler:
    """Base class for tool handlers."""

    def __init__(self, memory_service: MemoryService, formatter: MCPFormatter):
        self.memory_service = memory_service
        self.formatter = formatter

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle the tool call. Must be implemented by subclasses."""
        raise NotImplementedError


class SearchMemoriesHandler(ToolHandler):
    """Handler for search_memories tool."""

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        query = arguments.get("query", "")
        n_results = arguments.get("n_results", 5)

        if not query:
            return [TextContent(type="text", text="Error: Query parameter is required")]

        result = self.memory_service.search_memories(query, n_results)
        response_text = self.formatter.format_search_results(result, "all")
        return [TextContent(type="text", text=response_text)]


class SearchTextMemoriesHandler(ToolHandler):
    """Handler for search_text_memories tool."""

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        query = arguments.get("query", "")
        n_results = arguments.get("n_results", 5)

        if not query:
            return [TextContent(type="text", text="Error: Query parameter is required")]

        result = self.memory_service.search_text_memories_only(query, n_results)
        response_text = self.formatter.format_search_results(result, "text")
        return [TextContent(type="text", text=response_text)]


class SearchImageMemoriesHandler(ToolHandler):
    """Handler for search_image_memories tool."""

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        query = arguments.get("query", "")
        n_results = arguments.get("n_results", 5)

        if not query:
            return [TextContent(type="text", text="Error: Query parameter is required")]

        result = self.memory_service.search_image_memories_only(query, n_results)
        response_text = self.formatter.format_search_results(result, "image")
        return [TextContent(type="text", text=response_text)]


class SearchMemoriesByDateHandler(ToolHandler):
    """Handler for search_memories_by_date tool."""

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        query = arguments.get("query", "")
        start_date = arguments.get("start_date", "")
        end_date = arguments.get("end_date", None)
        n_results = arguments.get("n_results", 10)

        if not query or not start_date:
            return [TextContent(
                type="text",
                text="Error: Query and start_date parameters are required"
            )]

        result = self.memory_service.search_memories_by_date(
            query=query,
            start_date=start_date,
            end_date=end_date,
            n_results=n_results
        )
        response_text = self.formatter.format_date_search(result, start_date, end_date)
        return [TextContent(type="text", text=response_text)]


class SynthesizeMemoryStoryHandler(ToolHandler):
    """Handler for synthesize_memory_story tool."""

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        query = arguments.get("query", "")
        start_date = arguments.get("start_date", None)
        end_date = arguments.get("end_date", None)
        n_results_per_type = arguments.get("n_results_per_type", 10)

        if not query:
            return [TextContent(type="text", text="Error: Query parameter is required")]

        result = self.memory_service.synthesize_memories(
            query=query,
            start_date=start_date,
            end_date=end_date,
            n_results_per_type=n_results_per_type
        )
        response_text = self.formatter.format_synthesis(result)
        return [TextContent(type="text", text=response_text)]


class AddTextMemoryHandler(ToolHandler):
    """Handler for add_text_memory tool."""

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        text = arguments.get("text", "")
        title = arguments.get("title", "")
        tags = arguments.get("tags", "")
        description = arguments.get("description", "")

        if not text:
            return [TextContent(type="text", text="Error: Text parameter is required")]

        doc_id = self.memory_service.add_text_memory(
            text=text,
            title=title or None,
            tags=tags or None,
            description=description or None
        )

        return [TextContent(
            type="text",
            text=f"Successfully added text memory with ID: {doc_id}\n"
                 f"Title: {title if title else 'N/A'}\n"
                 f"Tags: {tags if tags else 'N/A'}"
        )]


class GetMemoryStatsHandler(ToolHandler):
    """Handler for get_memory_stats tool."""

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        stats = self.memory_service.get_memory_stats()
        response_text = self.formatter.format_stats(
            stats.text_count,
            stats.image_count,
            stats.total_count
        )
        return [TextContent(type="text", text=response_text)]


class ListRecentMemoriesHandler(ToolHandler):
    """Handler for list_recent_memories tool."""

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        limit = arguments.get("limit", 10)
        memory_type = arguments.get("memory_type", "all")

        memories = self.memory_service.list_recent_memories(limit, memory_type)
        response_text = self.formatter.format_recent_memories(memories, memory_type)
        return [TextContent(type="text", text=response_text)]


class ToolRegistry:
    """Registry for tool handlers using command pattern."""

    def __init__(self, memory_service: MemoryService, formatter: MCPFormatter):
        self.handlers: Dict[str, ToolHandler] = {
            "search_memories": SearchMemoriesHandler(memory_service, formatter),
            "search_text_memories": SearchTextMemoriesHandler(memory_service, formatter),
            "search_image_memories": SearchImageMemoriesHandler(memory_service, formatter),
            "search_memories_by_date": SearchMemoriesByDateHandler(memory_service, formatter),
            "synthesize_memory_story": SynthesizeMemoryStoryHandler(memory_service, formatter),
            "add_text_memory": AddTextMemoryHandler(memory_service, formatter),
            "get_memory_stats": GetMemoryStatsHandler(memory_service, formatter),
            "list_recent_memories": ListRecentMemoriesHandler(memory_service, formatter),
        }

    def handle(self, tool_name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Dispatch tool call to appropriate handler."""
        handler = self.handlers.get(tool_name)

        if not handler:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{tool_name}'"
            )]

        try:
            return handler.handle(arguments)
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error executing tool '{tool_name}': {str(e)}"
            )]

#!/usr/bin/env python3
"""MCP Server for Memory Map Application.

This server exposes memory search and management capabilities via the Model Context Protocol.
It uses stdio transport for local communication with AI tools like Claude Desktop.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types

from backend.services.memory_service import MemoryService
from backend.mcp_server.formatters import MCPFormatter
from backend.mcp_server.handlers import ToolRegistry
from backend.mcp_server.config import initialize_mcp_environment


# Initialize server
server = Server("memory-map")

# Global components (initialized in main)
memory_service: MemoryService = None
tool_registry: ToolRegistry = None


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for memory management."""
    return [
        Tool(
            name="search_memories",
            description="Search through both text and image memories using natural language. "
                       "Returns relevant memories ranked by semantic similarity. "
                       "Use this to find memories related to a specific topic, event, or concept. "
                       "NOTE: For more control, use search_text_memories or search_image_memories separately.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g., 'memories about my trip to Japan', 'photos of sunset')"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_text_memories",
            description="Search ONLY text memories (diary entries, notes, written reflections). "
                       "Use this when you specifically need text-based memories. "
                       "Returns memories ranked by semantic similarity to the query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query for text memories"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_image_memories",
            description="Search ONLY image memories (photos, screenshots, visual content). "
                       "Use this when you specifically need image-based memories. "
                       "Returns memories ranked by visual and semantic similarity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query for image memories"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_memories_by_date",
            description="Search memories within a specific date range. "
                       "Searches both text and images, filtering by date. "
                       "Useful for questions like 'what was I doing on October 15?' or 'show me memories from last week'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format or natural language (e.g., 'October 15', 'last Monday')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format or natural language (optional, defaults to start_date)"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["query", "start_date"]
            }
        ),
        Tool(
            name="synthesize_memory_story",
            description="AGENTIC TOOL: Synthesize memories from multiple sources into a coherent timeline story. "
                       "Searches both text and images, filters by date if specified, and creates a chronological narrative. "
                       "This is the MAIN tool for answering questions like 'what was I doing on [date]?' "
                       "It returns structured data ready for you to craft into a natural narrative.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query about memories (e.g., 'my activities on October 15')"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Optional start date filter (YYYY-MM-DD or natural language)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Optional end date filter (YYYY-MM-DD or natural language)"
                    },
                    "n_results_per_type": {
                        "type": "integer",
                        "description": "Number of results to fetch per memory type (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="add_text_memory",
            description="Add a new text-based memory to the system. "
                       "The memory will be embedded and made searchable. "
                       "Optionally include metadata like title, tags, and description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content of the memory"
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional title for the memory"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Optional comma-separated tags (e.g., 'travel, japan, 2024')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description or context about the memory"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_memory_stats",
            description="Get statistics about stored memories including total counts and breakdowns by type.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_recent_memories",
            description="List recently added memories. Returns both text and image memories in chronological order.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to return (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "memory_type": {
                        "type": "string",
                        "description": "Filter by memory type: 'text', 'image', or 'all' (default: 'all')",
                        "enum": ["text", "image", "all"],
                        "default": "all"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution requests using the tool registry."""
    if not arguments:
        arguments = {}

    return tool_registry.handle(name, arguments)


async def main():
    """Main entry point for the MCP server."""
    global memory_service, tool_registry

    # Initialize MCP environment and memory service
    try:
        # Initialize environment (creates directories, sets up config)
        config = initialize_mcp_environment()

        # Initialize memory service with configured paths
        memory_service = MemoryService(**config.get_memory_service_config())

        # Initialize formatter and tool registry
        formatter = MCPFormatter()
        tool_registry = ToolRegistry(memory_service, formatter)
    except Exception as e:
        print(f"Error initializing memory service: {e}", file=sys.stderr)
        sys.exit(1)

    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="memory-map",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())

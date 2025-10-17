#!/usr/bin/env python3
"""MCP Server for Memory Map Application.

This server exposes memory search and management capabilities via the Model Context Protocol.
It uses stdio transport for local communication with AI tools like Claude Desktop.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types

from services.memory_service import MemoryService


# Initialize server
server = Server("memory-map")

# Global components (initialized in main)
memory_service: MemoryService = None


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for memory management."""
    return [
        Tool(
            name="search_memories",
            description="Search through both text and image memories using natural language. "
                       "Returns relevant memories ranked by semantic similarity. "
                       "Use this to find memories related to a specific topic, event, or concept.",
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
    """Handle tool execution requests."""

    if not arguments:
        arguments = {}

    try:
        if name == "search_memories":
            query = arguments.get("query", "")
            n_results = arguments.get("n_results", 5)

            if not query:
                return [TextContent(
                    type="text",
                    text="Error: Query parameter is required"
                )]

            # Search using service
            result = memory_service.search_memories(query, n_results)

            if result.count == 0:
                return [TextContent(
                    type="text",
                    text=f"No memories found for query: '{query}'"
                )]

            # Format results
            response_text = f"Found {result.count} memories for '{query}':\n\n"

            for idx, memory in enumerate(result.memories, 1):
                metadata = memory.get('metadata', {})
                memory_type = metadata.get('type', 'unknown')
                distance = memory.get('distance', 'N/A')

                response_text += f"--- Memory {idx} ({memory_type}) ---\n"
                response_text += f"Relevance Score: {distance:.4f}\n"

                if metadata.get('title'):
                    response_text += f"Title: {metadata['title']}\n"

                if metadata.get('tags'):
                    response_text += f"Tags: {metadata['tags']}\n"

                if metadata.get('description'):
                    response_text += f"Description: {metadata['description']}\n"

                if memory_type == 'text':
                    text_content = metadata.get('text', memory.get('document', ''))
                    # Truncate long text
                    if len(text_content) > 500:
                        text_content = text_content[:500] + "..."
                    response_text += f"Content: {text_content}\n"
                elif memory_type == 'image':
                    response_text += f"Image Path: {metadata.get('source', 'N/A')}\n"

                response_text += "\n"

            return [TextContent(type="text", text=response_text)]

        elif name == "add_text_memory":
            text = arguments.get("text", "")
            title = arguments.get("title", "")
            tags = arguments.get("tags", "")
            description = arguments.get("description", "")

            if not text:
                return [TextContent(
                    type="text",
                    text="Error: Text parameter is required"
                )]

            # Add memory using service
            doc_id = memory_service.add_text_memory(
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

        elif name == "get_memory_stats":
            # Get stats using service
            stats = memory_service.get_memory_stats()

            response_text = f"Memory Statistics:\n\n"
            response_text += f"Total Memories: {stats.total_count}\n"
            response_text += f"├── Text Memories: {stats.text_count}\n"
            response_text += f"└── Image Memories: {stats.image_count}\n"

            return [TextContent(type="text", text=response_text)]

        elif name == "list_recent_memories":
            limit = arguments.get("limit", 10)
            memory_type = arguments.get("memory_type", "all")

            # Get memories using service
            memories = memory_service.list_recent_memories(limit, memory_type)

            if not memories:
                return [TextContent(
                    type="text",
                    text=f"No {memory_type} memories found."
                )]

            response_text = f"Recent {memory_type} memories (showing {len(memories)}):\n\n"

            for idx, memory in enumerate(memories, 1):
                metadata = memory.get('metadata', {})
                mem_type = metadata.get('type', 'unknown')

                response_text += f"--- Memory {idx} ({mem_type}) ---\n"

                if metadata.get('title'):
                    response_text += f"Title: {metadata['title']}\n"

                if metadata.get('tags'):
                    response_text += f"Tags: {metadata['tags']}\n"

                if metadata.get('description'):
                    response_text += f"Description: {metadata['description']}\n"

                if mem_type == 'text':
                    text_content = metadata.get('text', memory.get('document', ''))
                    if len(text_content) > 300:
                        text_content = text_content[:300] + "..."
                    response_text += f"Content: {text_content}\n"
                elif mem_type == 'image':
                    response_text += f"Image Path: {metadata.get('source', 'N/A')}\n"

                response_text += "\n"

            return [TextContent(type="text", text=response_text)]

        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool '{name}': {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server."""
    global memory_service

    # Initialize memory service
    try:
        memory_service = MemoryService()
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

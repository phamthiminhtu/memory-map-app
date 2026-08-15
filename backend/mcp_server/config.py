"""
MCP Server Configuration

This module handles configuration and initialization for the MCP server.
"""

import os
from pathlib import Path
from typing import Tuple


class MCPConfig:
    """Configuration manager for MCP server."""

    def __init__(self, project_root: Path = None):
        """
        Initialize MCP configuration.

        Args:
            project_root: Project root directory. If None, infers from __file__
        """
        if project_root is None:
            # Infer project root from this file's location
            # mcp_server/config.py -> go up one level to project root
            project_root = Path(__file__).parent.parent

        self.project_root = project_root
        self.data_root = project_root / 'data'
        self.text_persist_dir = self.data_root / 'chroma_text'
        self.image_persist_dir = self.data_root / 'chroma_image'

    def ensure_data_directories(self) -> None:
        """Create necessary data directories if they don't exist."""
        directories = [
            self.data_root,
            self.text_persist_dir,
            self.image_persist_dir
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_persist_directories(self) -> Tuple[str, str]:
        """
        Get persistence directories for text and image databases.

        Returns:
            Tuple of (text_persist_dir, image_persist_dir) as strings
        """
        return str(self.text_persist_dir), str(self.image_persist_dir)

    def get_memory_service_config(self) -> dict:
        """
        Get configuration dict for MemoryService initialization.

        Returns:
            Dict with text_persist_dir and image_persist_dir
        """
        text_dir, image_dir = self.get_persist_directories()
        return {
            'text_persist_dir': text_dir,
            'image_persist_dir': image_dir
        }


def initialize_mcp_environment() -> MCPConfig:
    """
    Initialize MCP server environment.

    This is the main entry point for setting up the MCP server environment.
    It creates necessary directories and returns a configured MCPConfig instance.

    Returns:
        MCPConfig instance with initialized directories

    Raises:
        OSError: If directory creation fails
    """
    config = MCPConfig()
    config.ensure_data_directories()
    return config

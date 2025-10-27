"""Pydantic models for memory-related API endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AddTextMemoryRequest(BaseModel):
    """Request model for adding a text memory."""
    text: str = Field(..., description="The text content of the memory", min_length=1)
    title: Optional[str] = Field(None, description="Optional title for the memory")
    tags: Optional[str] = Field(None, description="Optional comma-separated tags")
    description: Optional[str] = Field(None, description="Optional description")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Today I learned about FastAPI and how to build REST APIs.",
                "title": "Learning FastAPI",
                "tags": "programming, learning, fastapi",
                "description": "Notes from my FastAPI tutorial"
            }
        }


class AddTextMemoryResponse(BaseModel):
    """Response model for adding a text memory."""
    success: bool = Field(..., description="Whether the operation was successful")
    doc_id: str = Field(..., description="Unique document ID of the created memory")
    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "doc_id": "a1b2c3d4e5f6...",
                "message": "Text memory added successfully"
            }
        }


class AddImageMemoryResponse(BaseModel):
    """Response model for adding an image memory."""
    success: bool = Field(..., description="Whether the operation was successful")
    doc_id: str = Field(..., description="Unique document ID of the created memory")
    message: str = Field(..., description="Success message")
    image_path: str = Field(..., description="Path where the image was saved")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "doc_id": "a1b2c3d4e5f6...",
                "message": "Image memory added successfully",
                "image_path": "/uploads/image_123.jpg"
            }
        }


class SearchMemoriesRequest(BaseModel):
    """Request model for searching memories."""
    query: str = Field(..., description="Natural language search query", min_length=1)
    n_results: int = Field(5, description="Number of results to return", ge=1, le=20)
    memory_type: Optional[str] = Field(
        "all",
        description="Type of memories to search: 'text', 'image', or 'all'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "programming tutorials",
                "n_results": 10,
                "memory_type": "all"
            }
        }


class MemoryItem(BaseModel):
    """Model representing a single memory item."""
    doc_id: str = Field(..., description="Unique document ID")
    text: Optional[str] = Field(None, description="Text content (for text memories)")
    image: Optional[str] = Field(None, description="Image path (for image memories)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Memory metadata")
    similarity: Optional[float] = Field(None, description="Similarity score (for search results)")

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "a1b2c3d4e5f6...",
                "text": "Today I learned about FastAPI",
                "metadata": {
                    "type": "text",
                    "title": "Learning FastAPI",
                    "tags": "programming, learning",
                    "timestamp": "2025-10-27T10:30:00"
                },
                "similarity": 0.87
            }
        }


class SearchMemoriesResponse(BaseModel):
    """Response model for searching memories."""
    success: bool = Field(..., description="Whether the operation was successful")
    query: str = Field(..., description="The search query that was executed")
    count: int = Field(..., description="Number of results returned")
    memories: List[MemoryItem] = Field(..., description="List of matching memories")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "query": "programming tutorials",
                "count": 2,
                "memories": [
                    {
                        "doc_id": "a1b2c3...",
                        "text": "FastAPI tutorial notes",
                        "metadata": {"type": "text", "title": "FastAPI"},
                        "similarity": 0.92
                    }
                ]
            }
        }


class MemoryStatsResponse(BaseModel):
    """Response model for memory statistics."""
    success: bool = Field(..., description="Whether the operation was successful")
    total_count: int = Field(..., description="Total number of memories")
    text_count: int = Field(..., description="Number of text memories")
    image_count: int = Field(..., description="Number of image memories")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_count": 150,
                "text_count": 100,
                "image_count": 50
            }
        }


class ErrorResponse(BaseModel):
    """Response model for errors."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid request",
                "detail": "The provided text cannot be empty"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field("1.0.0", description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-27T10:30:00Z",
                "version": "1.0.0"
            }
        }

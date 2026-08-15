"""Pydantic models for API request/response schemas."""

from backend.api.models.memory import (
    AddTextMemoryRequest,
    AddTextMemoryResponse,
    AddImageMemoryResponse,
    SearchMemoriesRequest,
    SearchMemoriesResponse,
    MemoryStatsResponse,
    MemoryItem,
    ErrorResponse,
    HealthResponse
)

__all__ = [
    "AddTextMemoryRequest",
    "AddTextMemoryResponse",
    "AddImageMemoryResponse",
    "SearchMemoriesRequest",
    "SearchMemoriesResponse",
    "MemoryStatsResponse",
    "MemoryItem",
    "ErrorResponse",
    "HealthResponse"
]

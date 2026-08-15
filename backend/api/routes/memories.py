"""Memory management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, List
import os
import shutil
from datetime import datetime

from backend.services.memory_service import MemoryService
from backend.api.dependencies import get_memory_service
from backend.api.models import (
    AddTextMemoryRequest,
    AddTextMemoryResponse,
    AddImageMemoryResponse,
    SearchMemoriesRequest,
    SearchMemoriesResponse,
    MemoryStatsResponse,
    MemoryItem,
    ErrorResponse
)

router = APIRouter(prefix="/api/memories", tags=["memories"])


@router.post("/text", response_model=AddTextMemoryResponse, status_code=201)
async def add_text_memory(
    request: AddTextMemoryRequest,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    Add a new text memory.

    Args:
        request: Text memory details
        memory_service: Injected memory service

    Returns:
        AddTextMemoryResponse: Created memory details

    Raises:
        HTTPException: If memory creation fails
    """
    try:
        doc_id = memory_service.add_text_memory(
            text=request.text,
            title=request.title,
            tags=request.tags,
            description=request.description
        )

        return AddTextMemoryResponse(
            success=True,
            doc_id=doc_id,
            message="Text memory added successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add text memory: {str(e)}"
        )


@router.post("/image", response_model=AddImageMemoryResponse, status_code=201)
async def add_image_memory(
    file: UploadFile = File(..., description="Image file to upload"),
    title: Optional[str] = Form(None, description="Optional title"),
    tags: Optional[str] = Form(None, description="Optional comma-separated tags"),
    description: Optional[str] = Form(None, description="Optional description"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    Add a new image memory.

    This endpoint accepts multipart/form-data with an image file and optional metadata.

    Args:
        file: Uploaded image file
        title: Optional title
        tags: Optional tags
        description: Optional description
        memory_service: Injected memory service

    Returns:
        AddImageMemoryResponse: Created memory details

    Raises:
        HTTPException: If file type is invalid or upload fails
    """
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )

    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, safe_filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Add to memory service
        doc_id = memory_service.add_image_memory(
            image_path=file_path,
            title=title,
            tags=tags,
            description=description
        )

        return AddImageMemoryResponse(
            success=True,
            doc_id=doc_id,
            message="Image memory added successfully",
            image_path=file_path
        )
    except Exception as e:
        # Clean up file if memory creation failed
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to add image memory: {str(e)}"
        )


@router.post("/search", response_model=SearchMemoriesResponse)
async def search_memories(
    request: SearchMemoriesRequest,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    Search memories using natural language query.

    Args:
        request: Search parameters
        memory_service: Injected memory service

    Returns:
        SearchMemoriesResponse: Matching memories

    Raises:
        HTTPException: If search fails
    """
    try:
        # Route to appropriate search method based on memory_type
        if request.memory_type == "text":
            result = memory_service.search_text_memories_only(
                query=request.query,
                n_results=request.n_results
            )
        elif request.memory_type == "image":
            result = memory_service.search_image_memories_only(
                query=request.query,
                n_results=request.n_results
            )
        else:  # "all"
            result = memory_service.search_memories(
                query=request.query,
                n_results=request.n_results
            )

        # Convert to response format
        memory_items = []
        for memory in result.memories:
            memory_items.append(MemoryItem(
                doc_id=memory.get('doc_id', ''),
                text=memory.get('text'),
                image=memory.get('image'),
                metadata=memory.get('metadata', {}),
                similarity=memory.get('similarity')
            ))

        return SearchMemoriesResponse(
            success=True,
            query=result.query,
            count=result.count,
            memories=memory_items
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    Get statistics about stored memories.

    Args:
        memory_service: Injected memory service

    Returns:
        MemoryStatsResponse: Memory statistics

    Raises:
        HTTPException: If stats retrieval fails
    """
    try:
        stats = memory_service.get_memory_stats()

        return MemoryStatsResponse(
            success=True,
            total_count=stats.total_count,
            text_count=stats.text_count,
            image_count=stats.image_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/recent", response_model=SearchMemoriesResponse)
async def get_recent_memories(
    limit: int = 10,
    memory_type: str = "all",
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    Get recent memories.

    Args:
        limit: Maximum number of memories to return (1-50)
        memory_type: Type filter - "text", "image", or "all"
        memory_service: Injected memory service

    Returns:
        SearchMemoriesResponse: Recent memories

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Validate parameters
        limit = max(1, min(50, limit))

        memories = memory_service.list_recent_memories(
            limit=limit,
            memory_type=memory_type
        )

        # Convert to response format
        memory_items = []
        for memory in memories:
            memory_items.append(MemoryItem(
                doc_id=memory.get('doc_id', ''),
                text=memory.get('text'),
                image=memory.get('image'),
                metadata=memory.get('metadata', {})
            ))

        return SearchMemoriesResponse(
            success=True,
            query="recent",
            count=len(memory_items),
            memories=memory_items
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent memories: {str(e)}"
        )


@router.delete("/{doc_id}")
async def delete_memory(
    doc_id: str,
    memory_type: str = "text",
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    Delete a memory by ID.

    Args:
        doc_id: Document ID to delete
        memory_type: Type of memory - "text" or "image"
        memory_service: Injected memory service

    Returns:
        dict: Success status

    Raises:
        HTTPException: If deletion fails or memory not found
    """
    try:
        success = memory_service.delete_memory(doc_id=doc_id, memory_type=memory_type)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Memory with ID {doc_id} not found"
            )

        return {
            "success": True,
            "message": f"Memory {doc_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete memory: {str(e)}"
        )

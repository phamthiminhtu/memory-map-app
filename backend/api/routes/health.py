"""Health check endpoint."""

from fastapi import APIRouter
from datetime import datetime
from backend.api.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running.

    Returns:
        HealthResponse: API health status
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version="1.0.0"
    )

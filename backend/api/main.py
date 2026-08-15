"""FastAPI application for Memory Map backend."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from backend.api.routes import memories_router, health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Memory Map API",
    description="REST API for managing and searching text and image memories",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch unexpected errors.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors (Pydantic validation failures).

    Args:
        request: The incoming request
        exc: The validation error

    Returns:
        JSONResponse with validation error details
    """
    logger.warning(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "detail": exc.errors()
        }
    )


# Register routers
app.include_router(health_router)
app.include_router(memories_router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API welcome message and links
    """
    return {
        "message": "Memory Map API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("Memory Map API starting up...")
    logger.info("API documentation available at /docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Memory Map API shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

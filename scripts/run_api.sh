#!/bin/bash

# FastAPI Backend Run Script
# This script activates the virtual environment and starts the FastAPI server

# Activate virtual environment
source ~/workspace/memory-map-env/bin/activate

# Navigate to project root
cd "$(dirname "$0")"

# Set PYTHONPATH to include the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the FastAPI server
echo "Starting Memory Map FastAPI backend..."
echo "API documentation will be available at: http://localhost:8000/docs"
echo "Health check: http://localhost:8000/health"
echo ""

uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

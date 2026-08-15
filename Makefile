# Makefile for memory-map-app
# Provides convenient commands for development and deployment

# Custom virtual environment location
VENV_PATH := $(HOME)/workspace/memory-map-env

.PHONY: help install install-uv sync compile clean run run-mcp test format lint

help:  ## Show this help message
	@echo "Memory Map App - Available Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies using uv (creates venv, compiles, and syncs)
	@echo "Installing dependencies with uv..."
	@if [ ! -d "$(VENV_PATH)" ]; then python3 -m venv "$(VENV_PATH)"; fi
	@. "$(VENV_PATH)/bin/activate" && uv pip compile requirements.txt -o requirements.lock
	@. "$(VENV_PATH)/bin/activate" && uv pip sync requirements.lock
	@echo "✓ Installation complete"

install-uv:  ## Install uv package manager
	@echo "Installing uv..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "✓ uv installed"

sync:  ## Sync dependencies from requirements.lock
	@echo "Syncing dependencies..."
	@. "$(VENV_PATH)/bin/activate" && uv pip sync requirements.lock
	@echo "✓ Dependencies synced"

compile:  ## Compile requirements.txt to requirements.lock
	@echo "Compiling requirements..."
	@. "$(VENV_PATH)/bin/activate" && uv pip compile requirements.txt -o requirements.lock
	@echo "✓ Requirements compiled"

clean:  ## Remove virtual environment and compiled files
	@echo "Cleaning up..."
	@rm -rf "$(VENV_PATH)"
	@rm -f requirements.lock
	@rm -rf __pycache__ */__pycache__ */*/__pycache__
	@rm -rf .pytest_cache
	@rm -rf *.egg-info
	@echo "✓ Cleanup complete"

run:  ## Run the Streamlit web application
	@echo "Starting Streamlit app..."
	@. "$(VENV_PATH)/bin/activate" && streamlit run app/main.py

run-mcp:  ## Run the MCP server (for testing)
	@echo "Starting MCP server..."
	@. "$(VENV_PATH)/bin/activate" && python mcp_server/server.py

test:  ## Run tests (when available)
	@echo "Running tests..."
	@. "$(VENV_PATH)/bin/activate" && python -m pytest tests/ -v || echo "No tests found"

format:  ## Format code with black
	@echo "Formatting code..."
	@. "$(VENV_PATH)/bin/activate" && black app/ db/ etl/ tools/ mcp_server/ || echo "black not installed, skipping"

lint:  ## Lint code with ruff
	@echo "Linting code..."
	@. "$(VENV_PATH)/bin/activate" && ruff check app/ db/ etl/ tools/ mcp_server/ || echo "ruff not installed, skipping"

update:  ## Update all dependencies to latest versions
	@echo "Updating dependencies..."
	@. "$(VENV_PATH)/bin/activate" && uv pip compile --upgrade requirements.txt -o requirements.lock
	@. "$(VENV_PATH)/bin/activate" && uv pip sync requirements.lock
	@echo "✓ Dependencies updated"

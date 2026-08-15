#!/bin/bash
# Setup script for memory-map-app using uv package manager
# This script compiles requirements and installs dependencies

set -e  # Exit on error

# Custom virtual environment location
VENV_PATH="$HOME/workspace/memory-map-env"

echo "=========================================="
echo "Memory Map App - Setup Script (using uv)"
echo "=========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed."
    echo "Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  or visit: https://github.com/astral-sh/uv"
    exit 1
fi

echo "✓ uv is installed"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists at $VENV_PATH"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"
echo "✓ Virtual environment activated"
echo ""

# Compile requirements using uv
echo "Compiling requirements.in with uv..."
uv pip compile requirements.in -o requirements.txt
echo "✓ Requirements compiled to requirements.txt"
echo ""

# Install dependencies using uv
echo "Installing dependencies with uv..."
uv pip sync requirements.txt
echo "✓ Dependencies installed"
echo ""

# Verify installation
echo "Verifying installation..."
echo ""
echo "Installed packages:"
uv pip list
echo ""

echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source $VENV_PATH/bin/activate"
echo ""
echo "2. Run the Streamlit app:"
echo "   streamlit run app/main.py"
echo ""
echo "3. (Optional) Configure MCP server for Claude Desktop:"
echo "   See README.md for instructions"
echo ""

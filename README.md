# memory-map-app

**Note**: This repository was developed with the assistance of Claude Code and Cursor.

## Goals
Play around with unstructured data processing using vector databases (ChromaDB), multimodal embedding models and interactive web interfaces for memory retrieval with natural language.

## Idea

A personal memory mapping application that helps you organize and retrieve your memories (diary entries or photos) using AI-powered semantic search.

## Usage

1. Add memories through the web interface
2. Search for memories using natural language
3. View memory connections and relationships
4. Export and backup your memories

## Technology Stack

### Core Technologies
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) - Efficient storage and retrieval of high-dimensional embeddings
- **Web Framework**: [Streamlit](https://streamlit.io/) - Interactive Python web interface
- **Deep Learning Framework**: [PyTorch](https://pytorch.org/) - Neural network operations and model inference

### Embedding Models
- **Image Embeddings**: [OpenAI CLIP](https://github.com/openai/CLIP) (ViT-B/32) - Vision-language model for image understanding and cross-modal search
- **Text Embeddings**: [Sentence Transformers](https://www.sbert.net/) (all-MiniLM-L6-v2) - Semantic text embeddings optimized for similarity search

### Architecture Highlights
- **Multimodal Search**: Unified retrieval system across text and images
- **Semantic Similarity**: Cosine similarity-based ranking for relevant results
- **Persistent Storage**: ChromaDB collections with automatic embedding generation
- **Modular Design**: Separate loaders for different data types (text, images)

## Features

- Upload and process text and images
- Generate semantic embeddings for memories
- Search through memories using natural language
- **MCP Server Integration**: Expose memory search to AI tools via Model Context Protocol

## Setup

### Quick Setup with uv (Recommended)

We recommend using [uv](https://github.com/astral-sh/uv) for faster dependency management:

```bash
# Option 1: Run the automated setup script
./setup.sh

# Option 2: Use the Makefile
make install
```

The script will:
1. Create a virtual environment at `~/workspace/memory-map-env`
2. Compile dependencies with locked versions
3. Install all packages using uv (much faster than pip)

**Run the application:**
```bash
source ~/workspace/memory-map-env/bin/activate  # Activate the environment
streamlit run app/main.py
```

**Other useful commands:**
```bash
make run        # Run the Streamlit app
make run-mcp    # Run the MCP server
make clean      # Remove virtual environment
make update     # Update all dependencies
```

**Note:** The virtual environment is stored at `~/workspace/memory-map-env` (or `%USERPROFILE%\workspace\memory-map-env` on Windows) to keep it separate from the project directory.

### Manual Setup (Alternative)

If you prefer using pip:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app/main.py
```

### MCP Server Setup (Optional)

The MCP (Model Context Protocol) server allows external AI tools like Claude Desktop to search and manage your memories.

#### Prerequisites

Install MCP dependencies:
```bash
pip install mcp
```

#### Configure Claude Desktop

1. Locate your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the memory-map server configuration:
```json
{
  "mcpServers": {
    "memory-map": {
      "command": "/Users/tototus/workspace/memory-map-env/bin/python",
      "args": [
        "/Users/tototus/workspace/memory-map-app/mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/tototus/workspace/memory-map-app"
      }
    }
  }
}
```

**Important**: Update both paths to match your actual installation:
- `command`: Path to Python in your virtual environment (`~/workspace/memory-map-env/bin/python`)
- `args[0]`: Path to the MCP server script
- `env.PYTHONPATH`: Path to your project root directory

3. Restart Claude Desktop

4. The memory-map tools should now be available in Claude Desktop

#### Available MCP Tools

Once configured, Claude Desktop can use these tools:

- **`search_memories`** - Search through text and image memories using natural language
  - Parameters: `query` (string), `n_results` (integer, default: 5)

- **`add_text_memory`** - Add new text-based memories
  - Parameters: `text` (required), `title`, `tags`, `description` (optional)

- **`get_memory_stats`** - Get statistics about stored memories
  - No parameters required

- **`list_recent_memories`** - List recently added memories
  - Parameters: `limit` (integer, default: 10), `memory_type` (text/image/all)

#### Testing the MCP Server

You can test the server directly from the command line:

```bash
python mcp_server/server.py
```

The server will start and wait for MCP protocol messages via stdin/stdout.

#### Example Usage in Claude Desktop

Once configured, you can ask Claude:
- "Search my memories for trips to Japan"
- "Add a text memory about my meeting today with tags work, planning"
- "Show me my recent image memories"
- "How many memories do I have stored?"

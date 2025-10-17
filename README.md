# memory-map-app

**Note**: This repository was developed with the assistance of Claude Code and Cursor.

## Goals
Play around with unstructured data processing using vector databases (ChromaDB), multimodal embedding models and interactive web interfaces for memory retrieval with natural language.

## Idea

A personal memory mapping application that helps you organize and retrieve your memories (diary entries or photos) using AI-powered semantic search.

## Usage

1. Add memories through the web interface
2. Search for memories using natural language

## Features to implement
1. Own your data! Host it in your own drive/ storage
2. View memory connections and relationships
3. Export and backup your memories

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
- **Agentic Flow**: Intelligent multi-tool selection for complex queries
  - Date-aware memory synthesis
  - Chronological timeline creation
  - Automatic text/image search combination
  - Narrative story generation from memories

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

Once configured, Claude Desktop can use these tools with **agentic behavior** - Claude will intelligently select and combine tools based on your query:

**🤖 Primary Agentic Tools:**

- **`synthesize_memory_story`** ⭐ - The main agentic tool for narrative queries
  - Searches both text and images
  - Filters by date automatically
  - Creates chronological timelines
  - Perfect for: "What was I doing on October 15?", "Tell me about my week"
  - Parameters: `query` (required), `start_date`, `end_date`, `n_results_per_type`

- **`search_memories_by_date`** - Date-aware search across all memory types
  - Searches both text and images with temporal filtering
  - Useful for: "Find memories from last week", "Show me October 15"
  - Parameters: `query`, `start_date` (required), `end_date`, `n_results`

**🔍 Specialized Search Tools:**

- **`search_text_memories`** - Search ONLY text memories (diary entries, notes)
  - Parameters: `query` (string), `n_results` (integer, default: 5)

- **`search_image_memories`** - Search ONLY image memories (photos, screenshots)
  - Parameters: `query` (string), `n_results` (integer, default: 5)

- **`search_memories`** - Unified search (legacy, less agentic)
  - Parameters: `query` (string), `n_results` (integer, default: 5)

**📝 Memory Management Tools:**

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

Once configured, you can ask Claude natural questions and it will intelligently select the right tools:

**📅 Date-Based Queries (Agentic):**
- "What was I doing on October 15?" → Claude uses `synthesize_memory_story`
- "Tell me about my week" → Claude uses date range synthesis
- "Show me everything from last Monday" → Claude uses `search_memories_by_date`

**🎯 Specialized Searches:**
- "Find my work notes from September" → Claude uses `search_text_memories` with date filter
- "Show me photos from the park" → Claude uses `search_image_memories`
- "What did I write about AI?" → Claude uses `search_text_memories`

**📝 Memory Management:**
- "Add a note about today's meeting with tags work, planning"
- "How many memories do I have?" → Claude uses `get_memory_stats`
- "Show me my recent memories" → Claude uses `list_recent_memories`

**💡 Complex Narratives:**
- "Create a story of my October" → Claude uses synthesis with broad date range
- "What were the highlights of my week?" → Combines search and synthesis

See [examples/claude_desktop_usage.md](examples/claude_desktop_usage.md) for detailed examples.

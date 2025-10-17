# memory-map-app

A semi vibe coding project using Claude Code and Cursor.

## Goals
Play around with unstructured data processing using vector databases (ChromaDB), multimodal embedding models, interactive web interfaces for memory retrieval with natural language and MCP server for interacting with AI clients for complex interactions.

## Ideas

A personal memory mapping application that helps you:
- Track your memories (diary entries or photos) in a vector database.
- Use AI clients (Claude Desktop) to retrieve and connect related memories based on your queries.
- Provide neuroscience insights based on your memories.

## Features

- Upload and process text and images
- Generate semantic embeddings for memories
- Search through memories using natural language
- MCP Server Integration: Expose memory search to AI tools via Model Context Protocol
- Agentic Flow: LLM tool selection for complex queries
  - Date-aware memory synthesis
  - Chronological timeline creation
  - Automatic text/image search combination
  - Narrative story generation from memories


## Roadmap - future features

- Own your data! Host it in your own drive/storage. Connect Claude Desktop with Google Drive to host data (instead of using the local file system). The flow becomes: user inputs memories (text/photo) -> Claude Desktop chooses tool to use (upload_memory in this case) -> data is uploaded to user's Google Drive.
- Neuroscience knowledge integration: search the web for related/fun neuroscience facts related to the memories retrieved.
- Agentic flow has many levels; currently this project is at level 2. Aim for more sophisticated workflows in the future.
  - Level 1: Rule-based
  - Level 2: LLM tool selection: ```User input → LLM analyzes → Selects best tool → Executes → Output```
  - Level 3: Multi-step reasoning: ```User input → LLM plans → Calls tool A → Analyzes result → Calls tool B → Synthesizes → Output```
  - Level 4: Autonomous Agents: ```User goal → Agent plans → Executes tools → Evaluates → Re-plans → Repeats until goal met```



## Technology Stack

### Core Technologies
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) - Efficient storage and retrieval of high-dimensional embeddings
- **MCP Python**: [MCP Python](https://github.com/modelcontextprotocol/python-sdk) - MCP Server to interact with MCP Clients (Claude Desktop for this project)
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


## Setup

### Quick Setup Options

- Option 1: Run the automated setup script
```bash
./scripts/setup.sh
```

- Option 2: Use the Makefile
```bash
# Option 2: Use the Makefile
make install
```

Details at: [Getting started](https://github.com/phamthiminhtu/memory-map-app/blob/master/docs/setup/get_started.md)

### MCP Server Setup

Please refer to [MCP Server setup](https://github.com/phamthiminhtu/memory-map-app/blob/master/docs/setup/mcp_server.md) for more details.

# memory-map-app

A semi vibe coding project using Claude Code and Cursor.

## Goals
Play around with unstructured data processing using vector databases (ChromaDB), multimodal embedding models, interactive web interfaces for memory retrieval with natural language and an MCP server to handle complex interactions with AI clients.

## Ideas

A personal memory mapping application that helps you:
- Track your memories (diary entries or photos) in a vector database.
- Use AI clients (Claude Desktop) to retrieve and connect related memories based on your queries.
- Provide neuroscience insights based on your memories.

## Implemented features

- Upload and process text and images
- Generate semantic embeddings for memories
- Search through memories using natural language
- Visualize memory connections
- Secure and private storage

## Project Structure

```
memory_map/
│
├── app/                     # Streamlit frontend
│   ├── main.py             # Streamlit app
│   └── components.py       # Reusable UI components
│
├── data/                   # Store raw and processed data
│   ├── raw/               # Uploaded photos, journal text
│   └── processed/         # Embeddings, metadata, etc.
│
├── etl/                   # ETL pipeline for unstructured data
│   ├── embed_text.py      # Text embedding pipeline
│   ├── embed_image.py     # Image embedding pipeline
│   └── loader.py          # Load and save to vector DB
│
├── db/                    # Vector DB setup and interface
│   ├── faiss_index.py     # FAISS vector DB operations
│   └── utils.py           # Save/load helpers
│
├── utils/                 # General utility scripts
│   └── text_cleaning.py   # Preprocess text data
│
├── requirements.txt       # Python dependencies
└── README.md             # Project overview
```

## Setup

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

## Usage

1. Add memories through the web interface
2. Search for memories using natural language
3. View memory connections and relationships
4. Export and backup your memories

## License

MIT License 

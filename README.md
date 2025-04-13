<<<<<<< HEAD
# memory-map-app
=======
# Memory Map

A personal memory mapping application that helps you organize and retrieve your memories using AI-powered semantic search.

## Features

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
>>>>>>> ee26a13 (Initial commit / Upload current folder)

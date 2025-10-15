# memory-map-app

## Goals
Play around with unstructured data processing using vector databases (ChromaDB), multimodal embedding models and interactive web interfaces for intelligent memory retrieval.

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

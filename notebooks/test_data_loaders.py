#!/usr/bin/env python3

import sys
import os
import numpy as np
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from etl.data_loaders.base_loader import BaseDataLoader
from etl.data_loaders.text_loader import TextDataLoader
from etl.data_loaders.image_loader import ImageDataLoader
from db.chroma_db import ChromaDB

def test_text_loader():
    """Test the TextDataLoader functionality"""
    print("\n=== Testing Text Data Loader ===")
    
    # Initialize text loader
    text_loader = TextDataLoader(vector_db)
    
    # Create a sample text file
    sample_text = "This is a sample text for testing the text loader functionality."
    sample_text_path = Path('sample_text.txt')
    sample_text_path.write_text(sample_text)
    
    try:
        # Test text processing
        text_embedding = text_loader.process_data(str(sample_text_path))
        print(f"Text embedding shape: {text_embedding.shape}")
        
        # Test saving text memory
        metadata = {
            'title': 'Sample Text',
            'description': 'A test text file',
            'upload_to_drive': True,
            'drive_folder': 'Test/Text'
        }
        text_loader.save_text_memory(str(sample_text_path), metadata)
        print("Successfully saved text memory")
        
    finally:
        # Cleanup
        if sample_text_path.exists():
            sample_text_path.unlink()
            print("Cleaned up sample text file")

def test_image_loader():
    """Test the ImageDataLoader functionality"""
    print("\n=== Testing Image Data Loader ===")
    
    # Initialize image loader
    image_loader = ImageDataLoader(vector_db)
    
    # Test image processing (assuming you have a test image)
    test_image_path = 'sample_image.jpg'  # Replace with your test image path
    
    if not os.path.exists(test_image_path):
        print(f"Warning: Test image not found at {test_image_path}")
        return
    
    try:
        # Test image processing
        image_embedding = image_loader.process_data(test_image_path)
        print(f"Image embedding shape: {image_embedding.shape}")
        
        # Test saving image memory
        metadata = {
            'title': 'Sample Image',
            'description': 'A test image',
            'drive_folder': 'Test/Images'
        }
        image_loader.save_image_memory(test_image_path, metadata)
        print("Successfully saved image memory")
        
    except Exception as e:
        print(f"Error processing image: {e}")

def test_memory_retrieval():
    """Test memory retrieval functionality"""
    print("\n=== Testing Memory Retrieval ===")
    
    # Initialize text loader for query processing
    text_loader = TextDataLoader(vector_db)
    
    # Test retrieving memories using text query
    query_text = "sample test"
    query_embedding = text_loader.process_data(query_text)
    memories = text_loader.load_memories(query_embedding, k=2)
    
    print("\nRetrieved memories:")
    for memory in memories:
        print(f"\nType: {memory['metadata']['type']}")
        print(f"Title: {memory['metadata'].get('title', 'N/A')}")
        print(f"Description: {memory['metadata'].get('description', 'N/A')}")
        if memory['metadata']['type'] == 'text':
            print(f"Text content: {memory['text'][:100]}...")
        else:
            print(f"Image link: {memory['image']}")

def main():
    """Main function to run all tests"""
    print("Starting data loader tests...")
    
    # Initialize vector database with ChromaDB
    global vector_db
    vector_db = ChromaDB(persist_directory="data/vector_db")
    
    # Run tests
    test_text_loader()
    test_image_loader()
    test_memory_retrieval()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 
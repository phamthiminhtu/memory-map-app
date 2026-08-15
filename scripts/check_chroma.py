from backend.db.chroma_db import ChromaDB
import json

def main():
    # Initialize ChromaDB with the same directory as your image loader
    chroma_db = ChromaDB(persist_directory='data/images')
    
    # Get all memories
    memories = chroma_db.get_all_memories()
    print(f"Total number of memories: {len(memories)}")
    
    # Print details of each memory
    for i, memory in enumerate(memories):
        print(f"\nMemory {i+1}:")
        print(f"ID: {memory.get('id')}")
        print(f"Type: {memory.get('metadata', {}).get('type')}")
        print(f"Title: {memory.get('metadata', {}).get('title')}")
        print(f"Description: {memory.get('metadata', {}).get('description')}")
        print("-" * 50)

if __name__ == "__main__":
    main() 
from db.chroma_db import ChromaDB
import numpy as np
import uuid

def main():
    # Initialize ChromaDB
    chroma_db = ChromaDB(persist_directory='data/test_chroma')
    
    # Create a test embedding
    embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
    test_embedding = np.random.rand(embedding_dim).tolist()
    
    # Add a test memory
    doc_id = str(uuid.uuid4())
    test_memory = {
        'doc_id': doc_id,
        'text': 'This is a test document',
        'embedding': test_embedding,
        'metadata': {
            'type': 'text',
            'title': 'Test Document',
            'description': 'A test document for ChromaDB'
        }
    }
    
    # Add the memory to the database
    chroma_db.add_memory(test_memory)
    print(f"Added test memory with ID: {doc_id}")
    
    # Search for the memory
    query = "test document"
    results = chroma_db.search_memories(query, n_results=5)
    print(f"\nSearch results for '{query}':")
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"ID: {result.get('doc_id')}")
        print(f"Text: {result.get('text')}")
        print(f"Distance: {result.get('distance')}")
        
        # Check if embedding exists and its shape
        embedding = result.get('embedding')
        if embedding is not None:
            if isinstance(embedding, list):
                print(f"Embedding shape: {len(embedding)}")
            elif isinstance(embedding, np.ndarray):
                print(f"Embedding shape: {embedding.shape}")
        else:
            print("No embedding found")
    
    # Get all memories
    all_memories = chroma_db.get_all_memories()
    print(f"\nTotal number of memories: {len(all_memories)}")
    
    # Get the specific memory
    memory = chroma_db.get_memory(doc_id)
    if memory:
        print(f"\nRetrieved memory with ID: {doc_id}")
        print(f"Text: {memory.get('text')}")
        
        # Check if embedding exists and its shape
        embedding = memory.get('embedding')
        if embedding is not None:
            if isinstance(embedding, list):
                print(f"Embedding shape: {len(embedding)}")
            elif isinstance(embedding, np.ndarray):
                print(f"Embedding shape: {embedding.shape}")
        else:
            print("No embedding found")
    else:
        print(f"\nMemory with ID {doc_id} not found")

if __name__ == "__main__":
    main() 
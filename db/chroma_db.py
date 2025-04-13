import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
import json
from typing import List, Dict, Any, Optional
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChromaDB:
    def __init__(self, persist_directory: str = 'data/chroma'):
        """
        Initialize ChromaDB with persistence
        
        Args:
            persist_directory (str): Directory to store the database
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Use default embedding function (all-MiniLM-L6-v2)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Initialize collections
        self._init_collections()
        
        logger.info(f"ChromaDB initialized at {persist_directory}")
    
    def _init_collections(self):
        """Initialize or get existing collections"""
        try:
            # Get or create memories collection
            self.memories = self.client.get_or_create_collection(
                name="memories",
                embedding_function=self.embedding_function,
                metadata={
                    "hnsw:space": "cosine",
                    "description": "Collection for storing memories with text, image, and metadata",
                    "schema": {
                        "doc_id": "string",
                        "text": "string",
                        "image": "string",
                        "embedding": "float[]",
                        "metadata": "json"
                    }
                }
            )
            
            # Get or create user_memories collection
            self.user_memories = self.client.get_or_create_collection(
                name="user_memories",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("Collections initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing collections: {str(e)}")
            raise
    
    def add_memory(self, record: Dict[str, Any]) -> str:
        """
        Add a memory to the database
        
        Args:
            doc_id (str): Unique identifier for the memory
            text (str): The text content of the memory
            image (Optional[str]): URL or path to the image
            embedding (Optional[List[float]]): Pre-computed embedding vector
            metadata (Optional[Dict[str, Any]]): Additional metadata for the memory
            
        Returns:
            str: ID of the added memory
        """
        try:
            # If no embedding provided, generate one from the text
            if embedding is None:
                embedding = self.embedding_function([text])[0]
            
            # Prepare metadata
            full_metadata = {
                "doc_id": doc_id,
                "text": text,
                "image": image,
                "metadata": json.dumps(metadata) if isinstance(metadata, dict) else "{}"
            }
            
            # Add the record to the memories collection
            self.memories.add(
                documents=[text],
                embeddings=[embedding],
                ids=[doc_id],
                metadatas=[full_metadata]
            )
            
            logger.info(f"Inserted record with ID: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Error inserting record: {str(e)}")
            raise 
    
    
    def search_memories(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query
        
        Args:
            query (str): The search query
            n_results (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of similar memories with their metadata
        """
        try:
            results = self.memories.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                formatted_results.append({
                    'doc_id': metadata.get('doc_id', results['ids'][0][i]),
                    'text': metadata.get('text', results['documents'][0][i]),
                    'image': metadata.get('image', ''),
                    'embedding': results['embeddings'][0][i] if 'embeddings' in results else None,
                    'metadata': json.loads(metadata.get('metadata', '{}')),
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
            
            logger.info(f"Found {len(formatted_results)} similar memories")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            raise
    
    def get_memory(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID
        
        Args:
            doc_id (str): ID of the memory to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Memory data if found, None otherwise
        """
        try:
            result = self.memories.get(ids=[doc_id])
            if result['ids']:
                metadata = result['metadatas'][0]
                return {
                    'doc_id': metadata.get('doc_id', result['ids'][0]),
                    'text': metadata.get('text', result['documents'][0]),
                    'image': metadata.get('image', ''),
                    'embedding': result['embeddings'][0] if 'embeddings' in result else None,
                    'metadata': json.loads(metadata.get('metadata', '{}'))
                }
            return None
        except Exception as e:
            logger.error(f"Error getting memory: {str(e)}")
            raise

    
    def delete_memory(self, doc_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            doc_id (str): ID of the memory to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.memories.delete(ids=[doc_id])
            logger.info(f"Deleted memory with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            return False
    
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """
        Get all memories from the database
        
        Returns:
            List[Dict[str, Any]]: List of all memories
        """
        try:
            results = self.memories.get()
            
            formatted_results = []
            for i in range(len(results['ids'])):
                metadata = results['metadatas'][i]
                formatted_results.append({
                    'doc_id': metadata.get('doc_id', results['ids'][i]),
                    'text': metadata.get('text', results['documents'][i]),
                    'image': metadata.get('image', ''),
                    'embedding': results['embeddings'][i] if 'embeddings' in results else None,
                    'metadata': json.loads(metadata.get('metadata', '{}'))
                })
            
            logger.info(f"Retrieved {len(formatted_results)} memories")
            return formatted_results
        except Exception as e:
            logger.error(f"Error getting all memories: {str(e)}")
            raise
    
    def reset(self):
        """Reset the database by deleting all collections"""
        try:
            self.client.reset()
            self._init_collections()
            logger.info("Database reset successfully")
        except Exception as e:
            logger.error(f"Error resetting database: {str(e)}")
            raise
"""
ChromaDB vector store for CLIche memory system.

This module provides a vector store implementation using ChromaDB, adapted from mem0.

Made with ❤️ by Pink Pixel
"""
from typing import List, Dict, Any, Optional, Tuple, Union
import os
import logging
import numpy as np
from pathlib import Path
from pydantic import BaseModel

from ..config import VectorStoreConfig
from .base import BaseVectorStore

# Import ChromaDB conditionally to handle cases where it's not installed
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.api.models.Collection import Collection
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    

class OutputData(BaseModel):
    """Data model for ChromaDB output"""
    id: Optional[str]  # memory id
    score: Optional[float]  # similarity score
    payload: Optional[Dict]  # metadata
    content: Optional[str]  # document content


class ChromaVectorStore(BaseVectorStore):
    """
    Vector store implementation using ChromaDB.
    """
    
    def __init__(self, config: VectorStoreConfig):
        """
        Initialize the ChromaDB vector store.
        
        Args:
            config: Configuration for the vector store
        """
        super().__init__(config)
        self.client = None
        self.collection = None
        self.embedding_function = None
        self.collection_name = config.collection_name
        
        # Check if ChromaDB is installed
        if not CHROMA_AVAILABLE:
            self.logger.error("ChromaDB is not installed. Please install it with 'pip install chromadb'.")
            return
        
        # Initialize if possible
        self.initialize()
    
    def initialize(self) -> bool:
        """
        Initialize the ChromaDB client and collection.
        
        Returns:
            True if successful, False otherwise
        """
        if not CHROMA_AVAILABLE:
            self.logger.error("ChromaDB is not installed. Please install it with 'pip install chromadb'.")
            return False
        
        try:
            # Set up settings
            settings = Settings(anonymized_telemetry=False)
            
            # Create the client
            if self.config.host:
                # Use HTTP client if host is specified
                settings.chroma_server_host = self.config.host
                settings.chroma_server_http_port = self.config.port or 8000
                settings.chroma_api_impl = "chromadb.api.fastapi.FastAPI"
                self.client = chromadb.HttpClient(
                    host=self.config.host,
                    port=self.config.port or 8000
                )
            else:
                # Use persistent client if persist_directory is specified
                persist_directory = self.config.persist_directory
                if not persist_directory:
                    # Default to ~/.config/cliche/memory/chroma
                    config_dir = Path.home() / ".config" / "cliche" / "memory"
                    persist_directory = str(config_dir / "chroma")
                
                # Ensure directory exists
                os.makedirs(persist_directory, exist_ok=True)
                
                settings.persist_directory = persist_directory
                settings.is_persistent = True
                
                self.client = chromadb.PersistentClient(
                    path=persist_directory
                )
            
            # Create or get the collection
            self.collection = self.create_col(self.collection_name)
            
            # Set the flag
            self.is_initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            return False
    
    def create_col(self, name: str, vector_size: int = None, distance: str = "cosine") -> Collection:
        """
        Create a new collection or get an existing one.
        
        Args:
            name: Name of the collection
            vector_size: Size of the vectors
            distance: Distance metric to use (e.g., "cosine", "euclidean")
            
        Returns:
            The collection
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=name)
            self.logger.info(f"Using existing collection: {name}")
        except ValueError:
            # Create the collection if it doesn't exist
            self.logger.info(f"Creating new collection: {name}")
            collection = self.client.create_collection(
                name=name,
                metadata={"dimensions": self.config.dimensions or vector_size}
            )
        
        return collection
    
    def _parse_output(self, data: Dict) -> List[OutputData]:
        """
        Parse the output data from ChromaDB.
        
        Args:
            data: Output data from ChromaDB
            
        Returns:
            List of parsed output data
        """
        keys = ["ids", "distances", "metadatas", "documents"]
        values = []
        
        for key in keys:
            value = data.get(key, [])
            if isinstance(value, list) and value and isinstance(value[0], list):
                value = value[0]
            values.append(value)
        
        ids, distances, metadatas, documents = values
        max_length = max(len(v) for v in values if isinstance(v, list) and v is not None)
        
        result = []
        for i in range(max_length):
            # Convert distance to score: smaller distance = higher score
            # For cosine distance, the range is 0 to 2, where 0 is identical
            # Convert to a 0-1 score where 1 is identical
            distance = distances[i] if isinstance(distances, list) and distances and i < len(distances) else 0
            
            # Handle negative distances (which can happen with cosine distance in ChromaDB)
            # Normalize to a 0-1 range where higher is better
            if distance < 0:
                # For negative distances, we'll use a simple normalization
                # Assuming the range is roughly -2 to 0, map to 0.5 to 1.0
                score = 0.75 + (distance / 4)  # Maps -2 to 0.25, 0 to 0.75
            else:
                # For positive distances, smaller is better
                # Map 0 to 1.0, 2 to 0.0
                score = max(0, 1.0 - (distance / 2.0))
            
            entry = OutputData(
                id=ids[i] if isinstance(ids, list) and ids and i < len(ids) else None,
                score=score,
                payload=(metadatas[i] if isinstance(metadatas, list) and metadatas and i < len(metadatas) else None),
                content=(documents[i] if isinstance(documents, list) and documents and i < len(documents) else None),
            )
            result.append(entry)
        
        return result
    
    def add(
        self, 
        content: str, 
        embedding: np.ndarray, 
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        Add a memory to the vector store.
        
        Args:
            content: Memory content
            embedding: Embedding for the content
            metadata: Metadata for the memory
            memory_id: Optional ID for the memory. If None, a new ID will be generated.
            
        Returns:
            ID of the added memory
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Generate an ID if not provided
        if memory_id is None:
            memory_id = self.generate_id()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Convert numpy array to list for ChromaDB
        embedding_list = embedding.tolist()
        
        # Add the memory to ChromaDB
        try:
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding_list],
                documents=[content],
                metadatas=[metadata]
            )
            self.logger.debug(f"Added memory with ID: {memory_id}")
            return memory_id
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            raise
    
    def insert(
        self,
        vectors: List[list],
        payloads: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ):
        """
        Insert vectors into the collection.
        
        Args:
            vectors: List of vectors to insert
            payloads: List of payloads (metadata) for each vector
            ids: List of IDs for each vector
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [self.generate_id() for _ in range(len(vectors))]
        
        # Add the vectors to ChromaDB
        try:
            self.collection.add(
                ids=ids,
                embeddings=vectors,
                metadatas=payloads
            )
            self.logger.debug(f"Inserted {len(vectors)} vectors")
        except Exception as e:
            self.logger.error(f"Failed to insert vectors: {e}")
            raise
    
    def search(
        self,
        query_embedding: np.ndarray,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for memories by embedding.
        
        Args:
            query_embedding: Embedding to search for
            limit: Maximum number of results to return
            filter_metadata: Metadata to filter by
            min_score: Minimum similarity score (0 to 1)
            
        Returns:
            List of memories, each with id, content, metadata, and score
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Convert numpy array to list for ChromaDB
        embedding_list = query_embedding.tolist()
        
        # Prepare where clause for filtering
        where = None
        if filter_metadata:
            where = self._prepare_where_clause(filter_metadata)
        
        self.logger.debug(f"Searching ChromaDB with embedding of shape {query_embedding.shape}, limit={limit}, min_score={min_score}")
        
        # Search for memories
        try:
            results = self.collection.query(
                query_embeddings=[embedding_list],
                n_results=limit,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Parse the output
            output_data = self._parse_output(results)
            
            # Convert to memory format
            memories = []
            for item in output_data:
                # Skip if below minimum score
                if item.score < min_score:
                    self.logger.debug(f"Skipping result with score {item.score} (below min_score {min_score})")
                    continue
                
                memories.append({
                    "id": item.id,
                    "content": item.content,
                    "metadata": item.payload,
                    "score": item.score
                })
            
            self.logger.debug(f"Processed search results: {len(memories)} items after filtering")
            return memories
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            raise
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory by ID.
        
        Args:
            memory_id: ID of the memory to get
            
        Returns:
            Memory if found, None otherwise
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Get the memory from ChromaDB
        try:
            results = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            # Parse the output
            output_data = self._parse_output(results)
            
            # Check if memory was found
            if not output_data:
                return None
            
            item = output_data[0]
            
            # Convert embedding to numpy array if present
            embedding = None
            if "embeddings" in results and results["embeddings"]:
                embedding = np.array(results["embeddings"][0])
            
            return {
                "id": item.id,
                "content": item.content,
                "metadata": item.payload,
                "embedding": embedding
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory: {e}")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Delete the memory from ChromaDB
        try:
            self.collection.delete(ids=[memory_id])
            self.logger.debug(f"Deleted memory with ID: {memory_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete memory: {e}")
            return False
    
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update a memory.
        
        Args:
            memory_id: ID of the memory to update
            content: New content (if None, keep existing)
            embedding: New embedding (if None, keep existing)
            metadata: New metadata (if None, keep existing)
            
        Returns:
            True if successful, False otherwise
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Get the current memory to keep unchanged values
        current = self.get(memory_id)
        if not current:
            self.logger.warning(f"Memory not found for update: {memory_id}")
            return False
        
        # Prepare update values
        update_values = {}
        
        if content is not None:
            update_values["documents"] = [content]
        
        if embedding is not None:
            update_values["embeddings"] = [embedding.tolist()]
        
        if metadata is not None:
            # Merge new metadata with existing metadata
            new_metadata = {**current["metadata"], **metadata}
            update_values["metadatas"] = [new_metadata]
        
        # Skip update if no values to update
        if not update_values:
            self.logger.warning("No values to update")
            return True
        
        # Update the memory in ChromaDB
        try:
            self.collection.update(
                ids=[memory_id],
                **update_values
            )
            self.logger.debug(f"Updated memory with ID: {memory_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update memory: {e}")
            return False
    
    def count(self, filter_metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Count memories.
        
        Args:
            filter_metadata: Metadata to filter by
            
        Returns:
            Number of memories
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("ChromaDB is not initialized")
        
        # Prepare where clause for filtering
        where = None
        if filter_metadata:
            where = self._prepare_where_clause(filter_metadata)
        
        # Count memories
        try:
            # For now, we need to get all IDs and count them
            results = self.collection.get(
                where=where,
                include=[]
            )
            
            # Count the IDs
            return len(results.get("ids", []))
        except Exception as e:
            self.logger.error(f"Failed to count memories: {e}")
            return 0
    
    def _prepare_where_clause(self, filter_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a where clause for ChromaDB from filter metadata.
        
        Args:
            filter_metadata: Metadata to filter by
            
        Returns:
            Where clause for ChromaDB
        """
        # ChromaDB uses a specific format for where clauses
        where_clause = {}
        
        for key, value in filter_metadata.items():
            if isinstance(value, list):
                # For list values, use $in operator
                where_clause[key] = {"$in": value}
            elif isinstance(value, dict) and all(k.startswith('$') for k in value.keys()):
                # For operator dicts, use as is
                where_clause[key] = value
            else:
                # For simple values, use equality
                where_clause[key] = value
        
        return where_clause
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        This method is called when the vector store is no longer needed.
        """
        # Nothing to clean up for ChromaDB
        pass
    
    def get_collection_name(self) -> str:
        """
        Get the name of the collection.
        
        Returns:
            Collection name
        """
        return self.collection_name
    
    def collection_exists(self) -> bool:
        """
        Check if the collection exists.
        
        Returns:
            True if exists, False otherwise
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                return False
        
        # List collections and check if this one exists
        try:
            collections = self.client.list_collections()
            for collection in collections:
                if collection.name == self.collection_name:
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to check if collection exists: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                return []
        
        # List collections
        try:
            collections = self.client.list_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            self.logger.error(f"Failed to list collections: {e}")
            return []
            
    def delete_collection(self) -> bool:
        """
        Delete the collection.
        
        Returns:
            True if successful, False otherwise
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                return False
                
        # Delete the collection
        try:
            self.client.delete_collection(name=self.collection_name)
            self.logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete collection: {e}")
            return False
            
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection information
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                return {}
                
        # Get collection info
        try:
            collection = self.client.get_collection(name=self.collection_name)
            return {
                "name": collection.name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
        except Exception as e:
            self.logger.error(f"Failed to get collection info: {e}")
            return {}
            
    def list(self, filter_metadata: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all memories.
        
        Args:
            filter_metadata: Metadata to filter by
            limit: Maximum number of memories to return
            
        Returns:
            List of memories
        """
        # Check if initialized
        if not self.is_initialized:
            if not self.initialize():
                return []
                
        # Prepare where clause for filtering
        where = None
        if filter_metadata:
            where = self._prepare_where_clause(filter_metadata)
            
        # List memories
        try:
            results = self.collection.get(
                where=where,
                limit=limit,
                include=["documents", "metadatas", "embeddings"]
            )
            
            # Parse the output
            output_data = self._parse_output(results)
            
            # Convert to memory format
            memories = []
            for item in output_data:
                memory = {
                    "id": item.id,
                    "content": item.content,
                    "metadata": item.payload,
                }
                
                # Add embedding if available
                if "embeddings" in results and results["embeddings"]:
                    idx = output_data.index(item)
                    if idx < len(results["embeddings"]):
                        memory["embedding"] = np.array(results["embeddings"][idx])
                
                memories.append(memory)
            
            return memories
        except Exception as e:
            self.logger.error(f"Failed to list memories: {e}")
            return []
